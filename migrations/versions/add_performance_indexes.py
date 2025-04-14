"""
Añadir índices para mejorar rendimiento.

Revision ID: add_performance_indexes
Revises: <revision_id_anterior>
Create Date: 2023-07-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '<revision_id_anterior>'  # Reemplazar con el ID de la revisión anterior
branch_labels = None
depends_on = None


def upgrade():
    """Añadir índices para mejorar el rendimiento de consultas frecuentes."""
    # Índices para la tabla campaigns
    op.create_index('ix_campaigns_platform_status', 'campaigns', ['platform', 'status'], unique=False)
    op.create_index('ix_campaigns_created_at', 'campaigns', ['created_at'], unique=False)
    op.create_index('ix_campaigns_job_id', 'campaigns', ['job_id'], unique=False)
    op.create_index('ix_campaigns_segment_id', 'campaigns', ['segment_id'], unique=False)
    
    # Índices para la tabla meta_campaigns
    op.create_index('ix_meta_campaigns_status', 'meta_campaigns', ['status'], unique=False)
    op.create_index('ix_meta_campaigns_campaign_id', 'meta_campaigns', ['campaign_id'], unique=False)
    op.create_index('ix_meta_campaigns_external_id', 'meta_campaigns', ['external_id'], unique=False)
    
    # Índices para la tabla meta_ad_sets
    op.create_index('ix_meta_ad_sets_status', 'meta_ad_sets', ['status'], unique=False)
    op.create_index('ix_meta_ad_sets_meta_campaign_id', 'meta_ad_sets', ['meta_campaign_id'], unique=False)
    op.create_index('ix_meta_ad_sets_external_id', 'meta_ad_sets', ['external_id'], unique=False)
    
    # Índices para la tabla meta_ads
    op.create_index('ix_meta_ads_status', 'meta_ads', ['status'], unique=False)
    op.create_index('ix_meta_ads_meta_ad_set_id', 'meta_ads', ['meta_ad_set_id'], unique=False)
    op.create_index('ix_meta_ads_external_id', 'meta_ads', ['external_id'], unique=False)
    
    # Índices para la tabla meta_insights
    op.create_index('ix_meta_insights_date_start', 'meta_insights', ['date_start'], unique=False)
    op.create_index('ix_meta_insights_date_stop', 'meta_insights', ['date_stop'], unique=False)
    op.create_index('ix_meta_insights_meta_campaign_id', 'meta_insights', ['meta_campaign_id'], unique=False)
    op.create_index('ix_meta_insights_meta_ad_set_id', 'meta_insights', ['meta_ad_set_id'], unique=False)
    op.create_index('ix_meta_insights_meta_ad_id', 'meta_insights', ['meta_ad_id'], unique=False)
    op.create_index('ix_meta_insights_date_campaign_id', 'meta_insights', ['date_start', 'meta_campaign_id'], unique=False)
    
    # Índices para la tabla job_openings
    op.create_index('ix_job_openings_status', 'job_openings', ['status'], unique=False)
    op.create_index('ix_job_openings_created_at', 'job_openings', ['created_at'], unique=False)
    op.create_index('ix_job_openings_company_id', 'job_openings', ['company_id'], unique=False)
    
    # Índices para la tabla candidates
    op.create_index('ix_candidates_status', 'candidates', ['status'], unique=False)
    op.create_index('ix_candidates_created_at', 'candidates', ['created_at'], unique=False)
    op.create_index('ix_candidates_email', 'candidates', ['email'], unique=False)
    
    # Índices para la tabla applications
    op.create_index('ix_applications_status', 'applications', ['status'], unique=False)
    op.create_index('ix_applications_created_at', 'applications', ['created_at'], unique=False)
    op.create_index('ix_applications_job_id', 'applications', ['job_id'], unique=False)
    op.create_index('ix_applications_candidate_id', 'applications', ['candidate_id'], unique=False)
    op.create_index('ix_applications_job_candidate', 'applications', ['job_id', 'candidate_id'], unique=False)
    
    # Índices para la tabla segments
    op.create_index('ix_segments_status', 'segments', ['status'], unique=False)
    op.create_index('ix_segments_created_at', 'segments', ['created_at'], unique=False)


def downgrade():
    """Eliminar índices añadidos."""
    # Eliminar índices de la tabla campaigns
    op.drop_index('ix_campaigns_platform_status', table_name='campaigns')
    op.drop_index('ix_campaigns_created_at', table_name='campaigns')
    op.drop_index('ix_campaigns_job_id', table_name='campaigns')
    op.drop_index('ix_campaigns_segment_id', table_name='campaigns')
    
    # Eliminar índices de la tabla meta_campaigns
    op.drop_index('ix_meta_campaigns_status', table_name='meta_campaigns')
    op.drop_index('ix_meta_campaigns_campaign_id', table_name='meta_campaigns')
    op.drop_index('ix_meta_campaigns_external_id', table_name='meta_campaigns')
    
    # Eliminar índices de la tabla meta_ad_sets
    op.drop_index('ix_meta_ad_sets_status', table_name='meta_ad_sets')
    op.drop_index('ix_meta_ad_sets_meta_campaign_id', table_name='meta_ad_sets')
    op.drop_index('ix_meta_ad_sets_external_id', table_name='meta_ad_sets')
    
    # Eliminar índices de la tabla meta_ads
    op.drop_index('ix_meta_ads_status', table_name='meta_ads')
    op.drop_index('ix_meta_ads_meta_ad_set_id', table_name='meta_ads')
    op.drop_index('ix_meta_ads_external_id', table_name='meta_ads')
    
    # Eliminar índices de la tabla meta_insights
    op.drop_index('ix_meta_insights_date_start', table_name='meta_insights')
    op.drop_index('ix_meta_insights_date_stop', table_name='meta_insights')
    op.drop_index('ix_meta_insights_meta_campaign_id', table_name='meta_insights')
    op.drop_index('ix_meta_insights_meta_ad_set_id', table_name='meta_insights')
    op.drop_index('ix_meta_insights_meta_ad_id', table_name='meta_insights')
    op.drop_index('ix_meta_insights_date_campaign_id', table_name='meta_insights')
    
    # Eliminar índices de la tabla job_openings
    op.drop_index('ix_job_openings_status', table_name='job_openings')
    op.drop_index('ix_job_openings_created_at', table_name='job_openings')
    op.drop_index('ix_job_openings_company_id', table_name='job_openings')
    
    # Eliminar índices de la tabla candidates
    op.drop_index('ix_candidates_status', table_name='candidates')
    op.drop_index('ix_candidates_created_at', table_name='candidates')
    op.drop_index('ix_candidates_email', table_name='candidates')
    
    # Eliminar índices de la tabla applications
    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_created_at', table_name='applications')
    op.drop_index('ix_applications_job_id', table_name='applications')
    op.drop_index('ix_applications_candidate_id', table_name='applications')
    op.drop_index('ix_applications_job_candidate', table_name='applications')
    
    # Eliminar índices de la tabla segments
    op.drop_index('ix_segments_status', table_name='segments')
    op.drop_index('ix_segments_created_at', table_name='segments')
