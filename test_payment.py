"""
Script para probar el sistema de automatización de presupuesto.
"""

from adflux.models import BudgetPlan, PaymentMethod, Transaction
from adflux.core.factory import create_app
from adflux.services.payment_service import PaymentService

app = create_app()

with app.app_context():
    print("Probando sistema de automatización de presupuesto...")
    payment_service = PaymentService()
    
    print("\n1. Métodos de pago disponibles:")
    payment_methods = payment_service.get_payment_methods(user_id=1)
    if payment_methods:
        for method in payment_methods:
            print(f"- {method.type} **** {method.last_four} ({method.brand})")
    else:
        print("No hay métodos de pago registrados.")
        
        print("\nCreando método de pago de prueba...")
        success, message, method = payment_service.add_payment_method(
            user_id=1,
            payment_details={
                "card_number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123",
                "name": "Usuario Prueba"
            }
        )
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
    
    print("\n2. Planes de presupuesto:")
    budget_plans = payment_service.get_budget_plans(user_id=1)
    if budget_plans:
        for plan in budget_plans:
            print(f"- {plan.name}: ${plan.total_budget/100:.2f} ({plan.status})")
    else:
        print("No hay planes de presupuesto registrados.")
        
        print("\nCreando plan de presupuesto de prueba...")
        success, message, plan = payment_service.create_budget_plan(
            user_id=1,
            plan_data={
                "name": "Plan de prueba",
                "description": "Plan de presupuesto para pruebas",
                "total_budget": 10000,  # $100.00
                "distribution_type": "automatic",
                "daily_spend_limit": 1000,  # $10.00
                "alert_threshold": 80.0,  # Alerta al 80% del presupuesto
            }
        )
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
    
    print("\n3. Transacciones recientes:")
    transactions = payment_service.get_transactions(user_id=1, limit=5)
    if transactions:
        for tx in transactions:
            print(f"- {tx.transaction_type}: ${tx.amount/100:.2f} ({tx.status})")
    else:
        print("No hay transacciones registradas.")
        
        if budget_plans:
            plan_id = budget_plans[0].id
            print("\nCreando transacción de prueba...")
            success, message, tx = payment_service.create_transaction(
                user_id=1,
                transaction_data={
                    "budget_plan_id": plan_id,
                    "transaction_type": "charge",
                    "amount": 2500,  # $25.00
                    "description": "Cargo de prueba para campaña"
                }
            )
            print(f"Resultado: {'Éxito' if success else 'Error'}")
            print(f"Mensaje: {message}")
    
    print("\n4. Distribución automática de presupuesto:")
    if budget_plans:
        plan_id = budget_plans[0].id
        print(f"Distribuyendo presupuesto para plan {plan_id}...")
        success, message, distribution = payment_service.distribute_budget(
            plan_id=plan_id,
            campaign_ids=[1, 2, 3]  # IDs de campañas existentes
        )
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
        
        if success and distribution:
            print("\nDistribución generada:")
            for campaign_id, amount in distribution.items():
                print(f"- Campaña {campaign_id}: ${amount/100:.2f}")
    else:
        print("No hay planes de presupuesto para distribuir.")
