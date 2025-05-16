"""
Rutas para la gestión de pagos y presupuestos en AdFlux.

Este módulo define las rutas para gestionar métodos de pago, planes de presupuesto,
transacciones y redistribución automática de presupuesto.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, BooleanField, DateField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime, timedelta

from ..services import PaymentService, CampaignService
from ..api.common.logging import get_logger

logger = get_logger("payment_routes")

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

payment_service = PaymentService()
campaign_service = CampaignService()


class PaymentMethodForm(FlaskForm):
    """Formulario para añadir un método de pago."""
    
    payment_method_id = StringField("ID del método de pago", validators=[DataRequired()])
    set_default = BooleanField("Establecer como predeterminado", default=False)


class BudgetPlanForm(FlaskForm):
    """Formulario para crear o editar un plan de presupuesto."""
    
    name = StringField("Nombre del plan", validators=[DataRequired()])
    description = TextAreaField("Descripción", validators=[Optional()])
    total_budget = FloatField("Presupuesto total ($)", validators=[DataRequired(), NumberRange(min=1)])
    distribution_type = SelectField("Tipo de distribución", choices=[
        ("manual", "Manual"),
        ("automatic", "Automática"),
        ("performance_based", "Basada en rendimiento")
    ], validators=[DataRequired()])
    daily_spend_limit = FloatField("Límite de gasto diario ($)", validators=[Optional(), NumberRange(min=0)])
    alert_threshold = FloatField("Umbral de alerta (%)", validators=[Optional(), NumberRange(min=0, max=100)])
    start_date = DateField("Fecha de inicio", validators=[Optional()])
    end_date = DateField("Fecha de fin", validators=[Optional()])
    payment_method_id = SelectField("Método de pago", validators=[Optional()])
    initial_payment = FloatField("Pago inicial ($)", validators=[Optional(), NumberRange(min=0)])
    campaign_ids = SelectField("Campañas", validators=[Optional()], choices=[], render_kw={"multiple": True})


@payment_bp.route("/methods", methods=["GET"])
def payment_methods():
    """Renderiza la página de métodos de pago."""
    user_id = 1
    
    payment_methods = payment_service.get_payment_methods(user_id)
    
    form = PaymentMethodForm()
    
    return render_template(
        "payment/methods.html",
        payment_methods=payment_methods,
        form=form,
        stripe_enabled=payment_service.stripe_enabled
    )


@payment_bp.route("/methods/add", methods=["POST"])
def add_payment_method():
    """Procesa el formulario para añadir un método de pago."""
    user_id = 1
    
    form = PaymentMethodForm()
    
    if form.validate_on_submit():
        success, message, data = payment_service.add_payment_method(
            user_id=user_id,
            payment_method_id=form.payment_method_id.data
        )
        
        if success:
            if form.set_default.data and data and "id" in data:
                payment_service.set_default_payment_method(user_id, data["id"])
            
            flash(message, "success")
        else:
            flash(message, "error")
    else:
        flash("Error en el formulario. Por favor, revise los campos.", "error")
    
    return redirect(url_for("payment.payment_methods"))


@payment_bp.route("/methods/<int:payment_method_id>/default", methods=["POST"])
def set_default_payment_method(payment_method_id):
    """Establece un método de pago como predeterminado."""
    user_id = 1
    
    success, message = payment_service.set_default_payment_method(user_id, payment_method_id)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("payment.payment_methods"))


@payment_bp.route("/methods/<int:payment_method_id>/remove", methods=["POST"])
def remove_payment_method(payment_method_id):
    """Elimina un método de pago."""
    user_id = 1
    
    success, message = payment_service.remove_payment_method(user_id, payment_method_id)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("payment.payment_methods"))


@payment_bp.route("/budget-plans", methods=["GET"])
def budget_plans():
    """Renderiza la página de planes de presupuesto."""
    user_id = 1
    
    budget_plans = payment_service.get_budget_plans(user_id)
    
    return render_template(
        "payment/budget_plans.html",
        budget_plans=budget_plans
    )


@payment_bp.route("/budget-plans/create", methods=["GET", "POST"])
def create_budget_plan():
    """Renderiza y procesa el formulario para crear un plan de presupuesto."""
    user_id = 1
    
    form = BudgetPlanForm()
    
    payment_methods = payment_service.get_payment_methods(user_id)
    form.payment_method_id.choices = [(str(pm["id"]), f"{pm['brand']} **** {pm['last_four']}") for pm in payment_methods]
    form.payment_method_id.choices.insert(0, ("", "Seleccionar método de pago"))
    
    campaigns = campaign_service.get_campaigns()
    form.campaign_ids.choices = [(str(c.id), f"{c.name} ({c.platform})") for c in campaigns]
    
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description": form.description.data,
            "total_budget": form.total_budget.data,
            "distribution_type": form.distribution_type.data,
            "daily_spend_limit": form.daily_spend_limit.data,
            "alert_threshold": form.alert_threshold.data,
            "start_date": form.start_date.data.strftime("%Y-%m-%d") if form.start_date.data else None,
            "end_date": form.end_date.data.strftime("%Y-%m-%d") if form.end_date.data else None,
            "payment_method_id": int(form.payment_method_id.data) if form.payment_method_id.data else None,
            "initial_payment": form.initial_payment.data,
            "campaign_ids": [int(campaign_id) for campaign_id in request.form.getlist("campaign_ids")]
        }
        
        success, message, plan_data = payment_service.create_budget_plan(user_id, data)
        
        if success:
            flash(message, "success")
            return redirect(url_for("payment.budget_plans"))
        else:
            flash(message, "error")
    
    return render_template(
        "payment/budget_plan_form.html",
        form=form,
        action="create"
    )


@payment_bp.route("/budget-plans/<int:plan_id>", methods=["GET"])
def budget_plan_detail(plan_id):
    """Renderiza la página de detalle de un plan de presupuesto."""
    user_id = 1
    
    budget_plan = payment_service.get_budget_plan(user_id, plan_id)
    
    if not budget_plan:
        flash("Plan de presupuesto no encontrado", "error")
        return redirect(url_for("payment.budget_plans"))
    
    transactions = payment_service.get_transactions(
        user_id,
        filters={"budget_plan_id": plan_id}
    )
    
    return render_template(
        "payment/budget_plan_detail.html",
        budget_plan=budget_plan,
        transactions=transactions
    )


@payment_bp.route("/budget-plans/<int:plan_id>/edit", methods=["GET", "POST"])
def edit_budget_plan(plan_id):
    """Renderiza y procesa el formulario para editar un plan de presupuesto."""
    user_id = 1
    
    budget_plan = payment_service.get_budget_plan(user_id, plan_id)
    
    if not budget_plan:
        flash("Plan de presupuesto no encontrado", "error")
        return redirect(url_for("payment.budget_plans"))
    
    form = BudgetPlanForm()
    
    payment_methods = payment_service.get_payment_methods(user_id)
    form.payment_method_id.choices = [(str(pm["id"]), f"{pm['brand']} **** {pm['last_four']}") for pm in payment_methods]
    form.payment_method_id.choices.insert(0, ("", "Seleccionar método de pago"))
    
    campaigns = campaign_service.get_campaigns()
    form.campaign_ids.choices = [(str(c.id), f"{c.name} ({c.platform})") for c in campaigns]
    
    if request.method == "GET":
        form.name.data = budget_plan["name"]
        form.description.data = budget_plan["description"]
        form.total_budget.data = budget_plan["total_budget"]
        form.distribution_type.data = budget_plan["distribution_type"]
        form.daily_spend_limit.data = budget_plan["daily_spend_limit"]
        form.alert_threshold.data = budget_plan["alert_threshold"]
        
        if budget_plan["start_date"]:
            form.start_date.data = datetime.strptime(budget_plan["start_date"], "%Y-%m-%d")
        
        if budget_plan["end_date"]:
            form.end_date.data = datetime.strptime(budget_plan["end_date"], "%Y-%m-%d")
        
        selected_campaign_ids = [str(campaign["id"]) for campaign in budget_plan["campaigns"]]
        form.campaign_ids.data = selected_campaign_ids
    
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "description": form.description.data,
            "total_budget": form.total_budget.data,
            "distribution_type": form.distribution_type.data,
            "daily_spend_limit": form.daily_spend_limit.data,
            "alert_threshold": form.alert_threshold.data,
            "start_date": form.start_date.data.strftime("%Y-%m-%d") if form.start_date.data else None,
            "end_date": form.end_date.data.strftime("%Y-%m-%d") if form.end_date.data else None,
            "payment_method_id": int(form.payment_method_id.data) if form.payment_method_id.data else None,
            "additional_payment": form.initial_payment.data,  # Usar el campo initial_payment para pagos adicionales
            "campaign_ids": [int(campaign_id) for campaign_id in request.form.getlist("campaign_ids")]
        }
        
        success, message, updated_plan = payment_service.update_budget_plan(user_id, plan_id, data)
        
        if success:
            flash(message, "success")
            return redirect(url_for("payment.budget_plan_detail", plan_id=plan_id))
        else:
            flash(message, "error")
    
    return render_template(
        "payment/budget_plan_form.html",
        form=form,
        action="edit",
        plan_id=plan_id
    )


@payment_bp.route("/budget-plans/<int:plan_id>/redistribute", methods=["POST"])
def redistribute_budget(plan_id):
    """Redistribuye el presupuesto entre campañas basado en rendimiento."""
    user_id = 1
    
    success, message = payment_service.redistribute_budget(user_id, plan_id)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("payment.budget_plan_detail", plan_id=plan_id))


@payment_bp.route("/transactions", methods=["GET"])
def transactions():
    """Renderiza la página de transacciones."""
    user_id = 1
    
    filters = {}
    
    if request.args.get("budget_plan_id"):
        filters["budget_plan_id"] = int(request.args.get("budget_plan_id"))
    
    if request.args.get("status"):
        filters["status"] = request.args.get("status")
    
    if request.args.get("transaction_type"):
        filters["transaction_type"] = request.args.get("transaction_type")
    
    if request.args.get("date_from"):
        filters["date_from"] = request.args.get("date_from")
    
    if request.args.get("date_to"):
        filters["date_to"] = request.args.get("date_to")
    
    transactions = payment_service.get_transactions(user_id, filters)
    
    budget_plans = payment_service.get_budget_plans(user_id)
    
    return render_template(
        "payment/transactions.html",
        transactions=transactions,
        budget_plans=budget_plans,
        filters=filters
    )


@payment_bp.route("/api/payment-intent", methods=["POST"])
def create_payment_intent():
    """Crea un intent de pago para Stripe Elements."""
    user_id = 1
    
    data = request.get_json()
    
    if not data or "amount" not in data:
        return jsonify({"success": False, "message": "Monto requerido"}), 400
    
    amount = int(float(data.get("amount", 0)) * 100)
    
    if amount <= 0:
        return jsonify({"success": False, "message": "El monto debe ser mayor que cero"}), 400
    
    if payment_service.stripe_enabled:
        try:
            import stripe
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                metadata={"user_id": user_id}
            )
            
            return jsonify({
                "success": True,
                "client_secret": intent.client_secret
            })
            
        except Exception as e:
            logger.error(f"Error al crear intent de pago: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Error al crear intent de pago: {str(e)}"}), 500
    else:
        return jsonify({
            "success": True,
            "client_secret": f"pi_mock_{user_id}_{amount}_secret_mock",
            "mode": "simulated"
        })


@payment_bp.route("/api/webhook", methods=["POST"])
def stripe_webhook():
    """Procesa webhooks de Stripe."""
    if not payment_service.stripe_enabled:
        return jsonify({"success": True, "message": "Modo simulado, webhook ignorado"}), 200
    
    import stripe
    
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, payment_service.stripe_webhook_secret
        )
    except ValueError as e:
        logger.error(f"Error en webhook de Stripe (payload inválido): {str(e)}")
        return jsonify({"success": False, "message": "Payload inválido"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Error en webhook de Stripe (firma inválida): {str(e)}")
        return jsonify({"success": False, "message": "Firma inválida"}), 400
    
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        logger.info(f"Pago exitoso: {payment_intent.id}")
        
    
    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        logger.warning(f"Pago fallido: {payment_intent.id}")
        
    
    return jsonify({"success": True, "message": "Webhook procesado"}), 200
