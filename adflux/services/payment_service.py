"""
Servicio de pagos para AdFlux.

Este servicio maneja la integración con Stripe para procesar pagos,
gestionar métodos de pago y administrar presupuestos de campañas.
"""

import os
import logging
import stripe
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import random

from ..models import db, PaymentMethod, BudgetPlan, Transaction, SpendingReport, Campaign, budget_campaign_association
from ..api.common.logging import get_logger

stripe.api_key = os.getenv("STRIPE_API_KEY", "")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

logger = get_logger("PaymentService")


class PaymentService:
    """
    Servicio que gestiona pagos, presupuestos y métodos de pago para campañas publicitarias.
    """
    
    def __init__(self):
        """Inicializa el servicio de pagos."""
        self.stripe_enabled = bool(stripe.api_key)
        if not self.stripe_enabled:
            logger.warning("Stripe no está configurado. Se utilizará el modo simulado.")
    
    
    def get_payment_methods(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene los métodos de pago registrados para un usuario."""
        payment_methods = PaymentMethod.query.filter_by(user_id=user_id).all()
        
        result = []
        for pm in payment_methods:
            result.append({
                "id": pm.id,
                "type": pm.type,
                "last_four": pm.last_four,
                "brand": pm.brand,
                "exp_month": pm.exp_month,
                "exp_year": pm.exp_year,
                "is_default": pm.is_default
            })
        
        return result
    
    def add_payment_method(self, user_id: int, payment_method_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Añade un nuevo método de pago para un usuario."""
        try:
            if not self.stripe_enabled:
                payment_data = self._mock_payment_method_data(payment_method_id)
                stripe_customer_id = f"cus_mock_{random.randint(1000, 9999)}"
            else:
                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
                
                customer = self._get_or_create_stripe_customer(user_id)
                
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=customer.id
                )
                
                payment_data = {
                    "type": payment_method.type,
                    "last_four": payment_method.card.last4 if payment_method.type == "card" else None,
                    "brand": payment_method.card.brand if payment_method.type == "card" else None,
                    "exp_month": payment_method.card.exp_month if payment_method.type == "card" else None,
                    "exp_year": payment_method.card.exp_year if payment_method.type == "card" else None
                }
                stripe_customer_id = customer.id
            
            is_default = PaymentMethod.query.filter_by(user_id=user_id).count() == 0
            
            new_payment_method = PaymentMethod(
                user_id=user_id,
                stripe_payment_method_id=payment_method_id,
                stripe_customer_id=stripe_customer_id,
                type=payment_data.get("type", "card"),
                last_four=payment_data.get("last_four", "1234"),
                brand=payment_data.get("brand", "visa"),
                exp_month=payment_data.get("exp_month", 12),
                exp_year=payment_data.get("exp_year", 2030),
                is_default=is_default
            )
            
            db.session.add(new_payment_method)
            db.session.commit()
            
            return True, "Método de pago añadido con éxito", {
                "id": new_payment_method.id,
                "type": new_payment_method.type,
                "last_four": new_payment_method.last_four,
                "brand": new_payment_method.brand,
                "is_default": new_payment_method.is_default
            }
            
        except Exception as e:
            logger.error(f"Error al añadir método de pago: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al guardar el método de pago: {str(e)}", None
    
    def _mock_payment_method_data(self, payment_method_id: str) -> Dict[str, Any]:
        """Genera datos simulados para un método de pago."""
        card_brands = ["visa", "mastercard", "amex", "discover"]
        
        return {
            "type": "card",
            "last_four": "".join([str(random.randint(0, 9)) for _ in range(4)]),
            "brand": random.choice(card_brands),
            "exp_month": random.randint(1, 12),
            "exp_year": datetime.now().year + random.randint(1, 10)
        }
    
    def _get_or_create_stripe_customer(self, user_id: int) -> Any:
        """Obtiene o crea un cliente de Stripe para un usuario."""
        existing_payment_method = PaymentMethod.query.filter_by(user_id=user_id).first()
        
        if existing_payment_method and existing_payment_method.stripe_customer_id:
            try:
                return stripe.Customer.retrieve(existing_payment_method.stripe_customer_id)
            except stripe.error.StripeError:
                pass
        
        return stripe.Customer.create(
            metadata={"user_id": str(user_id)}
        )
    
    def set_default_payment_method(self, user_id: int, payment_method_id: int) -> Tuple[bool, str]:
        """Establece un método de pago como predeterminado."""
        try:
            payment_method = PaymentMethod.query.filter_by(
                id=payment_method_id, user_id=user_id
            ).first()
            
            if not payment_method:
                return False, "Método de pago no encontrado"
            
            PaymentMethod.query.filter_by(user_id=user_id).update({"is_default": False})
            
            payment_method.is_default = True
            
            db.session.commit()
            
            return True, "Método de pago predeterminado actualizado"
            
        except Exception as e:
            logger.error(f"Error al establecer método de pago predeterminado: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al actualizar el método de pago: {str(e)}"
    
    def remove_payment_method(self, user_id: int, payment_method_id: int) -> Tuple[bool, str]:
        """Elimina un método de pago."""
        try:
            payment_method = PaymentMethod.query.filter_by(
                id=payment_method_id, user_id=user_id
            ).first()
            
            if not payment_method:
                return False, "Método de pago no encontrado"
            
            pending_transactions = Transaction.query.filter_by(
                payment_method_id=payment_method_id,
                status="pending"
            ).count()
            
            if pending_transactions > 0:
                return False, "No se puede eliminar un método de pago con transacciones pendientes"
            
            if payment_method.is_default:
                other_payment_method = PaymentMethod.query.filter(
                    PaymentMethod.user_id == user_id,
                    PaymentMethod.id != payment_method_id
                ).first()
                
                if other_payment_method:
                    other_payment_method.is_default = True
            
            if self.stripe_enabled:
                stripe.PaymentMethod.detach(payment_method.stripe_payment_method_id)
            
            db.session.delete(payment_method)
            db.session.commit()
            
            return True, "Método de pago eliminado con éxito"
            
        except Exception as e:
            logger.error(f"Error al eliminar método de pago: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al eliminar el método de pago: {str(e)}"
    
    
    def create_budget_plan(self, user_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Crea un nuevo plan de presupuesto."""
        try:
            if not data.get("name"):
                return False, "El nombre del plan es requerido", None
            
            if not data.get("total_budget") or float(data.get("total_budget", 0)) <= 0:
                return False, "El presupuesto total debe ser mayor que cero", None
            
            total_budget_cents = int(float(data.get("total_budget", 0)) * 100)
            
            budget_plan = BudgetPlan(
                user_id=user_id,
                name=data.get("name"),
                description=data.get("description"),
                total_budget=total_budget_cents,
                distribution_type=data.get("distribution_type", "manual"),
                distribution_config=data.get("distribution_config"),
                daily_spend_limit=int(float(data.get("daily_spend_limit", 0)) * 100) if data.get("daily_spend_limit") else None,
                alert_threshold=data.get("alert_threshold"),
                start_date=datetime.strptime(data.get("start_date"), "%Y-%m-%d") if data.get("start_date") else None,
                end_date=datetime.strptime(data.get("end_date"), "%Y-%m-%d") if data.get("end_date") else None
            )
            
            db.session.add(budget_plan)
            
            if data.get("campaign_ids"):
                for campaign_id in data.get("campaign_ids"):
                    campaign = Campaign.query.get(campaign_id)
                    if campaign:
                        budget_plan.campaigns.append(campaign)
            
            db.session.commit()
            
            if data.get("payment_method_id") and data.get("initial_payment"):
                initial_payment_cents = int(float(data.get("initial_payment", 0)) * 100)
                
                if initial_payment_cents > 0:
                    self.process_payment(
                        user_id=user_id,
                        payment_method_id=data.get("payment_method_id"),
                        amount=initial_payment_cents,
                        description=f"Pago inicial para plan de presupuesto: {budget_plan.name}",
                        budget_plan_id=budget_plan.id
                    )
            
            return True, "Plan de presupuesto creado con éxito", {
                "id": budget_plan.id,
                "name": budget_plan.name,
                "total_budget": budget_plan.total_budget / 100,
                "status": budget_plan.status
            }
            
        except Exception as e:
            logger.error(f"Error al crear plan de presupuesto: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al crear el plan de presupuesto: {str(e)}", None
    
    def get_budget_plans(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene los planes de presupuesto de un usuario."""
        budget_plans = BudgetPlan.query.filter_by(user_id=user_id).all()
        
        result = []
        for plan in budget_plans:
            used_budget = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.budget_plan_id == plan.id,
                Transaction.transaction_type == "charge",
                Transaction.status == "completed"
            ).scalar() or 0
            
            remaining_budget = plan.total_budget - used_budget
            
            campaigns = []
            for campaign in plan.campaigns:
                campaigns.append({
                    "id": campaign.id,
                    "name": campaign.name,
                    "platform": campaign.platform,
                    "status": campaign.status
                })
            
            result.append({
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "total_budget": plan.total_budget / 100,
                "used_budget": used_budget / 100,
                "remaining_budget": remaining_budget / 100,
                "distribution_type": plan.distribution_type,
                "status": plan.status,
                "start_date": plan.start_date.strftime("%Y-%m-%d") if plan.start_date else None,
                "end_date": plan.end_date.strftime("%Y-%m-%d") if plan.end_date else None,
                "campaigns": campaigns
            })
        
        return result
    
    def get_budget_plan(self, user_id: int, plan_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un plan de presupuesto específico."""
        plan = BudgetPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return None
        
        used_budget = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.budget_plan_id == plan.id,
            Transaction.transaction_type == "charge",
            Transaction.status == "completed"
        ).scalar() or 0
        
        remaining_budget = plan.total_budget - used_budget
        
        transactions = []
        for transaction in Transaction.query.filter_by(budget_plan_id=plan.id).order_by(Transaction.created_at.desc()).limit(10):
            transactions.append({
                "id": transaction.id,
                "type": transaction.transaction_type,
                "amount": transaction.amount / 100,
                "status": transaction.status,
                "date": transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "description": transaction.description
            })
        
        campaigns = []
        for campaign in plan.campaigns:
            campaigns.append({
                "id": campaign.id,
                "name": campaign.name,
                "platform": campaign.platform,
                "status": campaign.status,
                "daily_budget": campaign.daily_budget / 100 if campaign.daily_budget else 0
            })
        
        return {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "total_budget": plan.total_budget / 100,
            "used_budget": used_budget / 100,
            "remaining_budget": remaining_budget / 100,
            "distribution_type": plan.distribution_type,
            "distribution_config": plan.distribution_config,
            "daily_spend_limit": plan.daily_spend_limit / 100 if plan.daily_spend_limit else None,
            "alert_threshold": plan.alert_threshold,
            "status": plan.status,
            "start_date": plan.start_date.strftime("%Y-%m-%d") if plan.start_date else None,
            "end_date": plan.end_date.strftime("%Y-%m-%d") if plan.end_date else None,
            "campaigns": campaigns,
            "transactions": transactions
        }
    
    def update_budget_plan(self, user_id: int, plan_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Actualiza un plan de presupuesto."""
        try:
            plan = BudgetPlan.query.filter_by(id=plan_id, user_id=user_id).first()
            
            if not plan:
                return False, "Plan de presupuesto no encontrado", None
            
            if "name" in data:
                plan.name = data["name"]
            
            if "description" in data:
                plan.description = data["description"]
            
            if "distribution_type" in data:
                plan.distribution_type = data["distribution_type"]
            
            if "distribution_config" in data:
                plan.distribution_config = data["distribution_config"]
            
            if "daily_spend_limit" in data and data["daily_spend_limit"] is not None:
                plan.daily_spend_limit = int(float(data["daily_spend_limit"]) * 100)
            
            if "alert_threshold" in data:
                plan.alert_threshold = data["alert_threshold"]
            
            if "status" in data:
                plan.status = data["status"]
            
            if "start_date" in data and data["start_date"]:
                plan.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
            
            if "end_date" in data and data["end_date"]:
                plan.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
            
            if "total_budget" in data and float(data["total_budget"]) > 0:
                new_budget_cents = int(float(data["total_budget"]) * 100)
                
                used_budget = db.session.query(db.func.sum(Transaction.amount)).filter(
                    Transaction.budget_plan_id == plan.id,
                    Transaction.transaction_type == "charge",
                    Transaction.status == "completed"
                ).scalar() or 0
                
                if new_budget_cents < used_budget:
                    return False, "El nuevo presupuesto no puede ser menor que el presupuesto ya utilizado", None
                
                plan.total_budget = new_budget_cents
            
            if "campaign_ids" in data:
                plan.campaigns = []
                
                for campaign_id in data["campaign_ids"]:
                    campaign = Campaign.query.get(campaign_id)
                    if campaign:
                        plan.campaigns.append(campaign)
            
            db.session.commit()
            
            if data.get("payment_method_id") and data.get("additional_payment"):
                additional_payment_cents = int(float(data.get("additional_payment", 0)) * 100)
                
                if additional_payment_cents > 0:
                    self.process_payment(
                        user_id=user_id,
                        payment_method_id=data.get("payment_method_id"),
                        amount=additional_payment_cents,
                        description=f"Pago adicional para plan de presupuesto: {plan.name}",
                        budget_plan_id=plan.id
                    )
            
            return True, "Plan de presupuesto actualizado con éxito", self.get_budget_plan(user_id, plan_id)
            
        except Exception as e:
            logger.error(f"Error al actualizar plan de presupuesto: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al actualizar el plan de presupuesto: {str(e)}", None
    
    
    def process_payment(self, user_id: int, payment_method_id: int, amount: int, description: str, budget_plan_id: Optional[int] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Procesa un pago con Stripe."""
        try:
            payment_method = PaymentMethod.query.filter_by(
                id=payment_method_id, user_id=user_id
            ).first()
            
            if not payment_method:
                return False, "Método de pago no encontrado", None
            
            transaction = Transaction(
                user_id=user_id,
                payment_method_id=payment_method_id,
                budget_plan_id=budget_plan_id,
                transaction_type="charge",
                amount=amount,
                status="pending",
                description=description
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            if not self.stripe_enabled:
                stripe_charge_id = f"ch_mock_{transaction.id}"
                receipt_url = None
                
                success = random.random() < 0.9
                
                if not success:
                    transaction.status = "failed"
                    db.session.commit()
                    return False, "Error simulado al procesar el pago", None
            else:
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency="usd",
                    payment_method=payment_method.stripe_payment_method_id,
                    customer=payment_method.stripe_customer_id,
                    confirm=True,
                    description=description
                )
                
                stripe_charge_id = payment_intent.id
                receipt_url = payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None
            
            transaction.status = "completed"
            transaction.stripe_transaction_id = stripe_charge_id
            transaction.stripe_receipt_url = receipt_url
            
            db.session.commit()
            
            return True, "Pago procesado con éxito", {
                "id": transaction.id,
                "amount": transaction.amount / 100,
                "status": transaction.status,
                "receipt_url": transaction.stripe_receipt_url
            }
            
        except Exception as e:
            logger.error(f"Error al procesar pago: {str(e)}", exc_info=True)
            db.session.rollback()
            
            if 'transaction' in locals() and transaction.id:
                try:
                    transaction = Transaction.query.get(transaction.id)
                    if transaction:
                        transaction.status = "failed"
                        transaction.metadata = {"error": str(e)}
                        db.session.commit()
                except:
                    pass
            
            return False, f"Error al procesar el pago: {str(e)}", None
    
    def get_transactions(self, user_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene las transacciones de un usuario con filtros opcionales."""
        query = Transaction.query.filter_by(user_id=user_id)
        
        if filters:
            if filters.get("budget_plan_id"):
                query = query.filter_by(budget_plan_id=filters.get("budget_plan_id"))
            
            if filters.get("status"):
                query = query.filter_by(status=filters.get("status"))
            
            if filters.get("transaction_type"):
                query = query.filter_by(transaction_type=filters.get("transaction_type"))
            
            if filters.get("date_from"):
                date_from = datetime.strptime(filters.get("date_from"), "%Y-%m-%d")
                query = query.filter(Transaction.created_at >= date_from)
            
            if filters.get("date_to"):
                date_to = datetime.strptime(filters.get("date_to"), "%Y-%m-%d")
                date_to = date_to + timedelta(days=1)  # Incluir todo el día
                query = query.filter(Transaction.created_at < date_to)
        
        query = query.order_by(Transaction.created_at.desc())
        
        if filters and filters.get("limit"):
            query = query.limit(filters.get("limit"))
        
        transactions = query.all()
        
        result = []
        for transaction in transactions:
            payment_method_info = None
            if transaction.payment_method:
                payment_method_info = {
                    "id": transaction.payment_method.id,
                    "type": transaction.payment_method.type,
                    "last_four": transaction.payment_method.last_four,
                    "brand": transaction.payment_method.brand
                }
            
            budget_plan_info = None
            if transaction.budget_plan:
                budget_plan_info = {
                    "id": transaction.budget_plan.id,
                    "name": transaction.budget_plan.name
                }
            
            result.append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "amount": transaction.amount / 100,
                "currency": transaction.currency,
                "status": transaction.status,
                "description": transaction.description,
                "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "receipt_url": transaction.stripe_receipt_url,
                "payment_method": payment_method_info,
                "budget_plan": budget_plan_info
            })
        
        return result
    
    
    def redistribute_budget(self, user_id: int, plan_id: int) -> Tuple[bool, str]:
        """Redistribuye automáticamente el presupuesto entre campañas basado en rendimiento."""
        try:
            plan = BudgetPlan.query.filter_by(id=plan_id, user_id=user_id).first()
            
            if not plan:
                return False, "Plan de presupuesto no encontrado"
            
            if plan.distribution_type != "automatic" and plan.distribution_type != "performance_based":
                return False, "Este plan no está configurado para redistribución automática"
            
            if not plan.campaigns:
                return False, "No hay campañas asociadas a este plan"
            
            campaign_performance = {}
            
            for campaign in plan.campaigns:
                metrics = self._get_campaign_performance_metrics(campaign.id)
                
                performance_score = self._calculate_performance_score(metrics)
                
                campaign_performance[campaign.id] = {
                    "campaign": campaign,
                    "metrics": metrics,
                    "performance_score": performance_score
                }
            
            total_score = sum(data["performance_score"] for data in campaign_performance.values())
            
            if total_score <= 0:
                equal_percentage = 100.0 / len(campaign_performance)
                for campaign_id, data in campaign_performance.items():
                    self._update_campaign_budget_allocation(plan.id, campaign_id, equal_percentage)
                
                return True, "Presupuesto distribuido equitativamente (sin datos de rendimiento)"
            
            for campaign_id, data in campaign_performance.items():
                percentage = (data["performance_score"] / total_score) * 100.0
                
                self._update_campaign_budget_allocation(plan.id, campaign_id, percentage)
            
            self._update_campaign_daily_budgets(plan)
            
            return True, "Presupuesto redistribuido con éxito basado en rendimiento"
            
        except Exception as e:
            logger.error(f"Error al redistribuir presupuesto: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Error al redistribuir el presupuesto: {str(e)}"
    
    def _get_campaign_performance_metrics(self, campaign_id: int) -> Dict[str, float]:
        """Obtiene métricas de rendimiento para una campaña."""
        report = SpendingReport.query.filter_by(
            campaign_id=campaign_id
        ).order_by(SpendingReport.report_date.desc()).first()
        
        if report:
            return {
                "impressions": report.impressions or 0,
                "clicks": report.clicks or 0,
                "conversions": report.conversions or 0,
                "spend": report.total_spend or 0,
                "ctr": report.clicks / report.impressions * 100 if report.impressions else 0,
                "conversion_rate": report.conversions / report.clicks * 100 if report.clicks else 0,
                "cpc": report.total_spend / report.clicks if report.clicks else 0,
                "cpa": report.total_spend / report.conversions if report.conversions else 0
            }
        
        return {
            "impressions": random.randint(100, 1000),
            "clicks": random.randint(5, 50),
            "conversions": random.randint(0, 5),
            "spend": random.randint(1000, 5000),  # En centavos
            "ctr": random.uniform(0.5, 5.0),
            "conversion_rate": random.uniform(1.0, 10.0),
            "cpc": random.uniform(0.5, 2.0) * 100,  # En centavos
            "cpa": random.uniform(5.0, 20.0) * 100  # En centavos
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calcula una puntuación de rendimiento basada en métricas."""
        weights = {
            "ctr": 0.3,
            "conversion_rate": 0.4,
            "cpc": 0.15,
            "cpa": 0.15
        }
        
        normalized_ctr = min(10.0, metrics["ctr"]) / 10.0  # Normalizar CTR a 0-1
        normalized_conv_rate = min(20.0, metrics["conversion_rate"]) / 20.0  # Normalizar tasa de conversión a 0-1
        
        normalized_cpc = 1.0 - min(1.0, metrics["cpc"] / 500.0)  # Normalizar CPC a 0-1 (invertido)
        normalized_cpa = 1.0 - min(1.0, metrics["cpa"] / 5000.0)  # Normalizar CPA a 0-1 (invertido)
        
        score = (
            normalized_ctr * weights["ctr"] +
            normalized_conv_rate * weights["conversion_rate"] +
            normalized_cpc * weights["cpc"] +
            normalized_cpa * weights["cpa"]
        )
        
        return max(0.01, score)
    
    def _update_campaign_budget_allocation(self, plan_id: int, campaign_id: int, allocation_percentage: float) -> None:
        """Actualiza la asignación de presupuesto para una campaña."""
        association = db.session.execute(
            db.select(budget_campaign_association).where(
                budget_campaign_association.c.budget_plan_id == plan_id,
                budget_campaign_association.c.campaign_id == campaign_id
            )
        ).first()
        
        if association:
            db.session.execute(
                budget_campaign_association.update().where(
                    budget_campaign_association.c.budget_plan_id == plan_id,
                    budget_campaign_association.c.campaign_id == campaign_id
                ).values(
                    allocation_percentage=allocation_percentage
                )
            )
        else:
            db.session.execute(
                budget_campaign_association.insert().values(
                    budget_plan_id=plan_id,
                    campaign_id=campaign_id,
                    allocation_percentage=allocation_percentage
                )
            )
        
        db.session.commit()
    
    def _update_campaign_daily_budgets(self, budget_plan: BudgetPlan) -> None:
        """Actualiza los presupuestos diarios de las campañas basado en la asignación."""
        daily_budget = budget_plan.daily_spend_limit or (budget_plan.total_budget / 30)  # Presupuesto para 30 días por defecto
        
        associations = db.session.execute(
            db.select(budget_campaign_association).where(
                budget_campaign_association.c.budget_plan_id == budget_plan.id
            )
        ).all()
        
        for assoc in associations:
            campaign_daily_budget = int(daily_budget * (assoc.allocation_percentage / 100.0))
            
            campaign = Campaign.query.get(assoc.campaign_id)
            if campaign:
                campaign.daily_budget = campaign_daily_budget
        
        db.session.commit()
