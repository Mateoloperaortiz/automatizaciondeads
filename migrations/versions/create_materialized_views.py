"""
Crear vistas materializadas para mejorar rendimiento.

Revision ID: create_materialized_views
Revises: add_performance_indexes
Create Date: 2023-07-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_materialized_views'
down_revision = 'add_performance_indexes'  # Reemplazar con el ID de la revisión anterior
branch_labels = None
depends_on = None


def upgrade():
    """Crear vistas materializadas para mejorar el rendimiento de consultas frecuentes."""
    # Vista materializada para métricas diarias de campañas
    op.execute("""
    CREATE MATERIALIZED VIEW campaign_daily_metrics AS
    SELECT
        date_trunc('day', date_start) as day,
        meta_campaign_id,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(spend) as total_spend,
        CASE WHEN SUM(impressions) > 0
             THEN (SUM(clicks)::float / SUM(impressions)) * 100
             ELSE 0 END as ctr,
        CASE WHEN SUM(clicks) > 0
             THEN SUM(spend) / SUM(clicks)
             ELSE 0 END as cpc,
        CASE WHEN SUM(impressions) > 0
             THEN (SUM(spend) / SUM(impressions)) * 1000
             ELSE 0 END as cpm
    FROM meta_insights
    GROUP BY day, meta_campaign_id;
    """)
    
    # Índice para la vista materializada
    op.execute("""
    CREATE INDEX ix_campaign_daily_metrics_day_campaign
    ON campaign_daily_metrics(day, meta_campaign_id);
    """)
    
    # Vista materializada para métricas mensuales de campañas
    op.execute("""
    CREATE MATERIALIZED VIEW campaign_monthly_metrics AS
    SELECT
        date_trunc('month', date_start) as month,
        meta_campaign_id,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(spend) as total_spend,
        CASE WHEN SUM(impressions) > 0
             THEN (SUM(clicks)::float / SUM(impressions)) * 100
             ELSE 0 END as ctr,
        CASE WHEN SUM(clicks) > 0
             THEN SUM(spend) / SUM(clicks)
             ELSE 0 END as cpc,
        CASE WHEN SUM(impressions) > 0
             THEN (SUM(spend) / SUM(impressions)) * 1000
             ELSE 0 END as cpm
    FROM meta_insights
    GROUP BY month, meta_campaign_id;
    """)
    
    # Índice para la vista materializada
    op.execute("""
    CREATE INDEX ix_campaign_monthly_metrics_month_campaign
    ON campaign_monthly_metrics(month, meta_campaign_id);
    """)
    
    # Vista materializada para métricas de campañas por plataforma
    op.execute("""
    CREATE MATERIALIZED VIEW platform_metrics AS
    SELECT
        c.platform,
        date_trunc('day', mi.date_start) as day,
        SUM(mi.impressions) as total_impressions,
        SUM(mi.clicks) as total_clicks,
        SUM(mi.spend) as total_spend,
        CASE WHEN SUM(mi.impressions) > 0
             THEN (SUM(mi.clicks)::float / SUM(mi.impressions)) * 100
             ELSE 0 END as ctr,
        CASE WHEN SUM(mi.clicks) > 0
             THEN SUM(mi.spend) / SUM(mi.clicks)
             ELSE 0 END as cpc,
        CASE WHEN SUM(mi.impressions) > 0
             THEN (SUM(mi.spend) / SUM(mi.impressions)) * 1000
             ELSE 0 END as cpm
    FROM meta_insights mi
    JOIN meta_campaigns mc ON mi.meta_campaign_id = mc.external_id
    JOIN campaigns c ON mc.campaign_id = c.id
    GROUP BY c.platform, day;
    """)
    
    # Índice para la vista materializada
    op.execute("""
    CREATE INDEX ix_platform_metrics_platform_day
    ON platform_metrics(platform, day);
    """)
    
    # Función para actualizar las vistas materializadas
    op.execute("""
    CREATE OR REPLACE FUNCTION refresh_materialized_views()
    RETURNS void AS $$
    BEGIN
        REFRESH MATERIALIZED VIEW campaign_daily_metrics;
        REFRESH MATERIALIZED VIEW campaign_monthly_metrics;
        REFRESH MATERIALIZED VIEW platform_metrics;
    END;
    $$ LANGUAGE plpgsql;
    """)


def downgrade():
    """Eliminar vistas materializadas."""
    # Eliminar función
    op.execute("DROP FUNCTION IF EXISTS refresh_materialized_views();")
    
    # Eliminar vistas materializadas
    op.execute("DROP MATERIALIZED VIEW IF EXISTS platform_metrics;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS campaign_monthly_metrics;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS campaign_daily_metrics;")
