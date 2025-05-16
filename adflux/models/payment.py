"""
Modelos de pago para AdFlux.

Este módulo contiene los modelos relacionados con pagos y presupuestos
para campañas publicitarias, incluyendo integración con Stripe.
"""

import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from . import db


class PaymentMethod(db.Model):
    """
    Modelo que representa un método de pago registrado en Stripe.
    
    Almacena información sobre tarjetas de crédito u otros métodos de pago
    que los usuarios han registrado para su uso en campañas publicitarias.
    """
    
    __tablename__ = "payment_methods"
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False, index=True)
    
    stripe_payment_method_id = db.Column(String(255), nullable=False, unique=True)
    stripe_customer_id = db.Column(String(255), nullable=False)
    
    type = db.Column(String(50), nullable=False)  # 'card', 'bank_account', etc.
    last_four = db.Column(String(4), nullable=True)  # Últimos 4 dígitos
    brand = db.Column(String(50), nullable=True)  # 'visa', 'mastercard', etc.
    exp_month = db.Column(Integer, nullable=True)
    exp_year = db.Column(Integer, nullable=True)
    is_default = db.Column(Boolean, default=False)
    
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    
    transactions = relationship("Transaction", back_populates="payment_method")
    
    def __repr__(self):
        return f"<PaymentMethod {self.id}: {self.type} **** {self.last_four}>"


class BudgetPlan(db.Model):
    """
    Modelo que representa un plan de presupuesto para campañas publicitarias.
    
    Define cómo se distribuirá el presupuesto entre diferentes campañas y plataformas,
    y establece límites de gasto.
    """
    
    __tablename__ = "budget_plans"
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False, index=True)
    name = db.Column(String(255), nullable=False)
    description = db.Column(String(500), nullable=True)
    
    total_budget = db.Column(Integer, nullable=False)  # ej., 100000 para $1,000.00
    
    distribution_type = db.Column(String(50), nullable=False, default="manual")  # 'manual', 'automatic', 'performance_based'
    distribution_config = db.Column(JSON, nullable=True)  # Configuración específica de distribución
    
    daily_spend_limit = db.Column(Integer, nullable=True)  # Límite diario en centavos
    alert_threshold = db.Column(Float, nullable=True)  # Porcentaje del presupuesto para alertas
    
    status = db.Column(String(50), nullable=False, default="active")  # 'active', 'paused', 'completed'
    
    start_date = db.Column(DateTime, nullable=True)
    end_date = db.Column(DateTime, nullable=True)
    
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    
    campaigns = relationship("Campaign", secondary="budget_campaign_association")
    transactions = relationship("Transaction", back_populates="budget_plan")
    
    def __repr__(self):
        return f"<BudgetPlan {self.id}: {self.name} (${self.total_budget/100:.2f})>"


budget_campaign_association = db.Table(
    "budget_campaign_association",
    db.Column("budget_plan_id", Integer, ForeignKey("budget_plans.id"), primary_key=True),
    db.Column("campaign_id", Integer, ForeignKey("campaigns.id"), primary_key=True),
    db.Column("allocation_percentage", Float, nullable=False, default=100.0),  # Porcentaje asignado a esta campaña
    db.Column("max_daily_spend", Integer, nullable=True),  # Límite diario específico para esta campaña
    db.Column("created_at", DateTime, default=datetime.datetime.utcnow),
)


class Transaction(db.Model):
    """
    Modelo que representa una transacción de pago.
    
    Registra todas las transacciones relacionadas con presupuestos de campañas,
    incluyendo cargos, reembolsos y ajustes.
    """
    
    __tablename__ = "transactions"
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False, index=True)
    
    budget_plan_id = db.Column(Integer, ForeignKey("budget_plans.id"), nullable=True)
    budget_plan = relationship("BudgetPlan", back_populates="transactions")
    
    payment_method_id = db.Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    
    transaction_type = db.Column(String(50), nullable=False)  # 'charge', 'refund', 'adjustment'
    amount = db.Column(Integer, nullable=False)  # Monto en centavos
    currency = db.Column(String(3), nullable=False, default="USD")
    status = db.Column(String(50), nullable=False)  # 'pending', 'completed', 'failed', 'refunded'
    
    stripe_transaction_id = db.Column(String(255), nullable=True, unique=True)
    stripe_receipt_url = db.Column(String(500), nullable=True)
    
    description = db.Column(String(500), nullable=True)
    transaction_metadata = db.Column(JSON, nullable=True)  # Renombrado de 'metadata' que es un nombre reservado en SQLAlchemy
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    
    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type} ${self.amount/100:.2f} ({self.status})>"


class SpendingReport(db.Model):
    """
    Modelo que representa un informe de gastos de campañas.
    
    Almacena datos agregados sobre gastos de campañas para análisis y reportes.
    """
    
    __tablename__ = "spending_reports"
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False, index=True)
    
    budget_plan_id = db.Column(Integer, ForeignKey("budget_plans.id"), nullable=True)
    campaign_id = db.Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    report_date = db.Column(DateTime, nullable=False, index=True)
    period_type = db.Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    
    total_spend = db.Column(Integer, nullable=False, default=0)  # Monto en centavos
    platform_spend = db.Column(JSON, nullable=True)  # Desglose por plataforma
    
    impressions = db.Column(Integer, nullable=True)
    clicks = db.Column(Integer, nullable=True)
    conversions = db.Column(Integer, nullable=True)
    
    cpm = db.Column(Float, nullable=True)  # Costo por mil impresiones
    cpc = db.Column(Float, nullable=True)  # Costo por clic
    cpa = db.Column(Float, nullable=True)  # Costo por adquisición
    
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    
    def __repr__(self):
        return f"<SpendingReport {self.id}: {self.report_date.strftime('%Y-%m-%d')} (${self.total_spend/100:.2f})>"
