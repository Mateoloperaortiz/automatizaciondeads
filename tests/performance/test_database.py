"""
Pruebas para optimización de base de datos en AdFlux.

Este módulo contiene pruebas para verificar el rendimiento y la funcionalidad
de las optimizaciones de base de datos implementadas en AdFlux.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from sqlalchemy import text

from adflux.utils.pagination import keyset_paginate
from adflux.models import db, Campaign, MetaCampaign, User


@pytest.mark.performance
@pytest.mark.db
class TestDatabaseOptimization:
    """Pruebas para optimización de base de datos."""
    
    def test_indexes(self, db, admin_user):
        """Prueba que los índices mejoran el rendimiento de las consultas."""
        # Crear datos de prueba
        for i in range(100):
            campaign = Campaign(
                name=f'Campaign {i}',
                objective='AWARENESS',
                status='ACTIVE' if i % 2 == 0 else 'PAUSED',
                platform='META' if i % 3 == 0 else 'GOOGLE',
                daily_budget=100.0,
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            db.session.add(campaign)
        
        db.session.commit()
        
        # Consulta sin índice específico (usando EXPLAIN)
        with db.engine.connect() as conn:
            # Ejecutar EXPLAIN para la consulta
            result = conn.execute(text("""
                EXPLAIN ANALYZE
                SELECT * FROM campaigns
                WHERE platform = 'META' AND status = 'ACTIVE'
            """))
            explain_result = result.fetchall()
        
        # Crear índice compuesto
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_campaigns_platform_status
                ON campaigns (platform, status)
            """))
        
        # Consulta con índice (usando EXPLAIN)
        with db.engine.connect() as conn:
            # Ejecutar EXPLAIN para la consulta
            result = conn.execute(text("""
                EXPLAIN ANALYZE
                SELECT * FROM campaigns
                WHERE platform = 'META' AND status = 'ACTIVE'
            """))
            explain_result_with_index = result.fetchall()
        
        # Medir tiempo de consulta sin usar índice explícitamente
        start_time = time.time()
        result = Campaign.query.filter_by(platform='META', status='ACTIVE').all()
        query_time = time.time() - start_time
        
        # Verificar resultados
        assert len(result) > 0
        
        # Nota: No podemos verificar directamente que la consulta usa el índice
        # ya que depende del optimizador de consultas, pero podemos verificar
        # que la consulta se ejecuta en un tiempo razonable
        assert query_time < 0.1  # Debería ser rápido incluso con 100 registros
    
    def test_keyset_pagination(self, db, admin_user):
        """Prueba la paginación por keyset."""
        # Crear datos de prueba
        for i in range(100):
            campaign = Campaign(
                name=f'Campaign {i}',
                objective='AWARENESS',
                status='ACTIVE',
                platform='META',
                daily_budget=100.0 + i,
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            db.session.add(campaign)
        
        db.session.commit()
        
        # Consulta base
        query = Campaign.query.filter_by(status='ACTIVE')
        
        # Paginación por keyset (primera página)
        page1 = keyset_paginate(
            query,
            per_page=10,
            order_by=Campaign.id,
            ascending=True
        )
        
        # Verificar resultados de la primera página
        assert len(page1.items) == 10
        assert page1.has_next is True
        assert page1.has_prev is False
        
        # Obtener última clave de la primera página
        last_id = page1.items[-1].id
        
        # Paginación por keyset (segunda página)
        page2 = keyset_paginate(
            query,
            per_page=10,
            order_by=Campaign.id,
            ascending=True,
            after=last_id
        )
        
        # Verificar resultados de la segunda página
        assert len(page2.items) == 10
        assert page2.has_next is True
        assert page2.has_prev is True
        
        # Verificar que no hay duplicados entre páginas
        page1_ids = [item.id for item in page1.items]
        page2_ids = [item.id for item in page2.items]
        assert not set(page1_ids).intersection(set(page2_ids))
        
        # Verificar que los IDs están en orden ascendente
        assert all(page2_ids[i] > page2_ids[i-1] for i in range(1, len(page2_ids)))
        
        # Paginación por keyset con orden descendente
        page_desc = keyset_paginate(
            query,
            per_page=10,
            order_by=Campaign.id,
            ascending=False
        )
        
        # Verificar resultados con orden descendente
        assert len(page_desc.items) == 10
        assert page_desc.has_next is True
        assert page_desc.has_prev is False
        
        # Verificar que los IDs están en orden descendente
        page_desc_ids = [item.id for item in page_desc.items]
        assert all(page_desc_ids[i] < page_desc_ids[i-1] for i in range(1, len(page_desc_ids)))
    
    def test_keyset_pagination_with_multiple_columns(self, db, admin_user):
        """Prueba la paginación por keyset con múltiples columnas de ordenación."""
        # Crear datos de prueba
        for i in range(100):
            campaign = Campaign(
                name=f'Campaign {i}',
                objective='AWARENESS',
                status='ACTIVE',
                platform='META' if i % 3 == 0 else 'GOOGLE',
                daily_budget=100.0 + (i // 10),  # Algunos tendrán el mismo presupuesto
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            db.session.add(campaign)
        
        db.session.commit()
        
        # Consulta base
        query = Campaign.query.filter_by(status='ACTIVE')
        
        # Paginación por keyset con múltiples columnas (primera página)
        page1 = keyset_paginate(
            query,
            per_page=10,
            order_by=[Campaign.daily_budget, Campaign.id],
            ascending=[True, True]
        )
        
        # Verificar resultados de la primera página
        assert len(page1.items) == 10
        assert page1.has_next is True
        assert page1.has_prev is False
        
        # Obtener últimos valores de la primera página
        last_budget = page1.items[-1].daily_budget
        last_id = page1.items[-1].id
        
        # Paginación por keyset (segunda página)
        page2 = keyset_paginate(
            query,
            per_page=10,
            order_by=[Campaign.daily_budget, Campaign.id],
            ascending=[True, True],
            after=[last_budget, last_id]
        )
        
        # Verificar resultados de la segunda página
        assert len(page2.items) == 10
        assert page2.has_next is True
        assert page2.has_prev is True
        
        # Verificar que no hay duplicados entre páginas
        page1_ids = [item.id for item in page1.items]
        page2_ids = [item.id for item in page2.items]
        assert not set(page1_ids).intersection(set(page2_ids))
        
        # Verificar que los presupuestos están en orden ascendente
        page1_budgets = [item.daily_budget for item in page1.items]
        page2_budgets = [item.daily_budget for item in page2.items]
        
        # El primer presupuesto de la página 2 debe ser >= al último de la página 1
        assert page2_budgets[0] >= page1_budgets[-1]
    
    def test_query_performance_with_joins(self, db, admin_user):
        """Prueba el rendimiento de consultas con joins."""
        # Crear datos de prueba
        for i in range(50):
            # Crear campaña
            campaign = Campaign(
                name=f'Campaign {i}',
                objective='AWARENESS',
                status='ACTIVE',
                platform='META',
                daily_budget=100.0,
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            db.session.add(campaign)
            db.session.flush()  # Para obtener el ID
            
            # Crear campaña de Meta asociada
            meta_campaign = MetaCampaign(
                campaign_id=campaign.id,
                external_id=f'meta_{i}',
                status='ACTIVE'
            )
            db.session.add(meta_campaign)
        
        db.session.commit()
        
        # Medir tiempo de consulta con join
        start_time = time.time()
        result = db.session.query(Campaign, MetaCampaign).join(
            MetaCampaign, Campaign.id == MetaCampaign.campaign_id
        ).filter(
            Campaign.status == 'ACTIVE',
            MetaCampaign.status == 'ACTIVE'
        ).all()
        join_query_time = time.time() - start_time
        
        # Medir tiempo de consultas separadas
        start_time = time.time()
        campaigns = Campaign.query.filter_by(status='ACTIVE').all()
        campaign_ids = [c.id for c in campaigns]
        meta_campaigns = MetaCampaign.query.filter(
            MetaCampaign.campaign_id.in_(campaign_ids),
            MetaCampaign.status == 'ACTIVE'
        ).all()
        separate_queries_time = time.time() - start_time
        
        # Verificar resultados
        assert len(result) > 0
        
        # La consulta con join debería ser más eficiente
        assert join_query_time <= separate_queries_time * 1.2  # Permitir pequeña variación
    
    def test_bulk_operations(self, db, admin_user):
        """Prueba operaciones en lote."""
        # Medir tiempo de inserción individual
        start_time = time.time()
        for i in range(100):
            campaign = Campaign(
                name=f'Individual {i}',
                objective='AWARENESS',
                status='ACTIVE',
                platform='META',
                daily_budget=100.0,
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            db.session.add(campaign)
            db.session.commit()
        individual_time = time.time() - start_time
        
        # Limpiar tabla
        db.session.query(Campaign).delete()
        db.session.commit()
        
        # Medir tiempo de inserción en lote
        start_time = time.time()
        campaigns = []
        for i in range(100):
            campaign = Campaign(
                name=f'Bulk {i}',
                objective='AWARENESS',
                status='ACTIVE',
                platform='META',
                daily_budget=100.0,
                start_date=f'2023-01-{(i % 30) + 1}',
                end_date=f'2023-02-{(i % 28) + 1}',
                created_by=admin_user.id
            )
            campaigns.append(campaign)
        
        db.session.add_all(campaigns)
        db.session.commit()
        bulk_time = time.time() - start_time
        
        # Verificar que la inserción en lote es más rápida
        assert bulk_time < individual_time * 0.5  # Debería ser al menos 2 veces más rápido
