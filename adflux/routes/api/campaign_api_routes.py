"""
Rutas de API para campañas.

Este módulo define las rutas de API para gestionar campañas publicitarias.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import desc

from ...models import db, Campaign, MetaCampaign, MetaInsight
from ...utils.pagination import keyset_paginate, paginate_query, get_pagination_links
from ...utils.decorators import handle_exceptions, log_execution_time, rate_limit
from ...exceptions import ResourceNotFoundError, ValidationError


# Crear blueprint
campaign_api = Blueprint('campaign_api', __name__)


@campaign_api.route('/campaigns', methods=['GET'])
@handle_exceptions()
@log_execution_time
@rate_limit(limit=100, period=60)
def get_campaigns():
    """
    Obtiene una lista paginada de campañas.
    
    Query params:
        cursor: Cursor para keyset pagination
        page: Número de página para offset pagination
        per_page: Elementos por página
        status: Filtrar por estado
        platform: Filtrar por plataforma
        sort: Campo para ordenar (created_at, name, status)
        order: Dirección de ordenamiento (asc, desc)
        
    Returns:
        Respuesta JSON con lista de campañas y metadatos de paginación
    """
    # Obtener parámetros de consulta
    cursor = request.args.get('cursor')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    platform = request.args.get('platform')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Validar parámetros
    if per_page > 100:
        per_page = 100
    
    # Construir consulta base
    query = Campaign.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Campaign.status == status)
    if platform:
        query = query.filter(Campaign.platform == platform)
    
    # Determinar columna de ordenamiento
    if sort == 'name':
        sort_column = Campaign.name
    elif sort == 'status':
        sort_column = Campaign.status
    else:
        sort_column = Campaign.created_at
    
    # Determinar dirección de ordenamiento
    ascending = order.lower() == 'asc'
    
    # Aplicar paginación
    if cursor:
        # Usar keyset pagination para conjuntos de datos grandes
        pagination = keyset_paginate(
            query=query,
            column=sort_column,
            cursor=cursor,
            per_page=per_page,
            ascending=ascending
        )
    else:
        # Usar offset pagination para conjuntos de datos pequeños
        pagination = paginate_query(
            query=query.order_by(desc(sort_column) if not ascending else sort_column),
            page=page,
            per_page=per_page
        )
    
    # Serializar resultados
    campaigns = []
    for campaign in pagination.items:
        campaigns.append({
            'id': campaign.id,
            'name': campaign.name,
            'status': campaign.status,
            'platform': campaign.platform,
            'objective': campaign.objective,
            'daily_budget': campaign.daily_budget,
            'lifetime_budget': campaign.lifetime_budget,
            'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
            'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None,
        })
    
    # Generar enlaces de paginación
    links = get_pagination_links(
        endpoint='campaign_api.get_campaigns',
        pagination=pagination,
        status=status,
        platform=platform,
        sort=sort,
        order=order
    )
    
    # Construir respuesta
    response = {
        'data': campaigns,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_cursor': pagination.next_cursor,
            'prev_cursor': pagination.prev_cursor
        },
        'links': links
    }
    
    return jsonify(response)


@campaign_api.route('/campaigns/<int:campaign_id>', methods=['GET'])
@handle_exceptions()
@log_execution_time
def get_campaign(campaign_id):
    """
    Obtiene una campaña por su ID.
    
    Args:
        campaign_id: ID de la campaña
        
    Returns:
        Respuesta JSON con datos de la campaña
    """
    # Obtener campaña
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        raise ResourceNotFoundError(f"Campaña con ID {campaign_id} no encontrada")
    
    # Obtener campaña de Meta asociada
    meta_campaign = MetaCampaign.query.filter_by(campaign_id=campaign_id).first()
    
    # Obtener métricas de rendimiento
    metrics = {}
    if meta_campaign:
        # Usar vista materializada para métricas
        metrics_query = db.session.execute(
            """
            SELECT
                SUM(total_impressions) as impressions,
                SUM(total_clicks) as clicks,
                SUM(total_spend) as spend,
                AVG(ctr) as ctr,
                AVG(cpc) as cpc,
                AVG(cpm) as cpm
            FROM campaign_daily_metrics
            WHERE meta_campaign_id = :campaign_id
            """,
            {"campaign_id": meta_campaign.external_id}
        )
        
        metrics_row = metrics_query.fetchone()
        if metrics_row:
            metrics = {
                'impressions': int(metrics_row[0] or 0),
                'clicks': int(metrics_row[1] or 0),
                'spend': float(metrics_row[2] or 0.0),
                'ctr': float(metrics_row[3] or 0.0),
                'cpc': float(metrics_row[4] or 0.0),
                'cpm': float(metrics_row[5] or 0.0)
            }
    
    # Serializar campaña
    campaign_data = {
        'id': campaign.id,
        'name': campaign.name,
        'status': campaign.status,
        'platform': campaign.platform,
        'objective': campaign.objective,
        'daily_budget': campaign.daily_budget,
        'lifetime_budget': campaign.lifetime_budget,
        'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
        'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
        'job_id': campaign.job_id,
        'segment_id': campaign.segment_id,
        'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
        'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None,
        'metrics': metrics,
        'meta_campaign': {
            'id': meta_campaign.id,
            'external_id': meta_campaign.external_id,
            'status': meta_campaign.status
        } if meta_campaign else None
    }
    
    return jsonify(campaign_data)


@campaign_api.route('/campaigns/<int:campaign_id>/insights', methods=['GET'])
@handle_exceptions()
@log_execution_time
def get_campaign_insights(campaign_id):
    """
    Obtiene insights de rendimiento para una campaña.
    
    Args:
        campaign_id: ID de la campaña
        
    Query params:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        group_by: Agrupación (day, week, month)
        
    Returns:
        Respuesta JSON con insights de rendimiento
    """
    # Obtener parámetros de consulta
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    group_by = request.args.get('group_by', 'day')
    
    # Validar parámetros
    if not start_date or not end_date:
        raise ValidationError("Se requieren los parámetros start_date y end_date")
    
    try:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    except ValueError:
        raise ValidationError("Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Validar agrupación
    if group_by not in ['day', 'week', 'month']:
        group_by = 'day'
    
    # Obtener campaña
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        raise ResourceNotFoundError(f"Campaña con ID {campaign_id} no encontrada")
    
    # Obtener campaña de Meta asociada
    meta_campaign = MetaCampaign.query.filter_by(campaign_id=campaign_id).first()
    if not meta_campaign:
        return jsonify({
            'insights': [],
            'summary': {
                'impressions': 0,
                'clicks': 0,
                'spend': 0.0,
                'ctr': 0.0,
                'cpc': 0.0,
                'cpm': 0.0
            }
        })
    
    # Construir consulta SQL según la agrupación
    if group_by == 'day':
        date_trunc = 'day'
        view_name = 'campaign_daily_metrics'
    elif group_by == 'week':
        date_trunc = 'week'
        view_name = 'campaign_daily_metrics'
    else:  # month
        view_name = 'campaign_monthly_metrics'
        date_trunc = 'month'
    
    # Consultar insights agrupados
    if view_name == 'campaign_monthly_metrics':
        insights_query = db.session.execute(
            f"""
            SELECT
                month as date,
                total_impressions as impressions,
                total_clicks as clicks,
                total_spend as spend,
                ctr,
                cpc,
                cpm
            FROM campaign_monthly_metrics
            WHERE meta_campaign_id = :campaign_id
            AND month >= :start_date
            AND month <= :end_date
            ORDER BY month
            """,
            {
                "campaign_id": meta_campaign.external_id,
                "start_date": start_date,
                "end_date": end_date
            }
        )
    else:
        insights_query = db.session.execute(
            f"""
            SELECT
                date_trunc('{date_trunc}', day) as date,
                SUM(total_impressions) as impressions,
                SUM(total_clicks) as clicks,
                SUM(total_spend) as spend,
                CASE WHEN SUM(total_impressions) > 0
                     THEN (SUM(total_clicks)::float / SUM(total_impressions)) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(total_clicks) > 0
                     THEN SUM(total_spend) / SUM(total_clicks)
                     ELSE 0 END as cpc,
                CASE WHEN SUM(total_impressions) > 0
                     THEN (SUM(total_spend) / SUM(total_impressions)) * 1000
                     ELSE 0 END as cpm
            FROM {view_name}
            WHERE meta_campaign_id = :campaign_id
            AND day >= :start_date
            AND day <= :end_date
            GROUP BY date_trunc('{date_trunc}', day)
            ORDER BY date_trunc('{date_trunc}', day)
            """,
            {
                "campaign_id": meta_campaign.external_id,
                "start_date": start_date,
                "end_date": end_date
            }
        )
    
    # Procesar resultados
    insights = []
    total_impressions = 0
    total_clicks = 0
    total_spend = 0.0
    
    for row in insights_query:
        date_str = row[0].strftime('%Y-%m-%d')
        impressions = int(row[1] or 0)
        clicks = int(row[2] or 0)
        spend = float(row[3] or 0.0)
        ctr = float(row[4] or 0.0)
        cpc = float(row[5] or 0.0)
        cpm = float(row[6] or 0.0)
        
        insights.append({
            'date': date_str,
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'ctr': ctr,
            'cpc': cpc,
            'cpm': cpm
        })
        
        total_impressions += impressions
        total_clicks += clicks
        total_spend += spend
    
    # Calcular métricas totales
    summary = {
        'impressions': total_impressions,
        'clicks': total_clicks,
        'spend': total_spend,
        'ctr': (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0,
        'cpc': total_spend / total_clicks if total_clicks > 0 else 0.0,
        'cpm': (total_spend / total_impressions) * 1000.0 if total_impressions > 0 else 0.0
    }
    
    return jsonify({
        'insights': insights,
        'summary': summary
    })
