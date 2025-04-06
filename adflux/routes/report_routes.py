"""
Rutas de informes para AdFlux.

Este módulo contiene las rutas relacionadas con la generación de informes.
"""

from flask import Blueprint, render_template, request, current_app, jsonify, send_file
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
import io
import os
from ..models import db, Campaign, JobOpening, Candidate, MetaInsight
from ..extensions import csrf
from flask_wtf.csrf import generate_csrf

# Definir el blueprint
report_bp = Blueprint('report', __name__, template_folder='../templates')


@report_bp.route('/reports')
def reports_dashboard():
    """Renderiza la página principal de informes."""
    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()
    
    # Obtener parámetros de consulta para filtrado
    report_type = request.args.get('type', 'campaign')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Establecer fechas predeterminadas si no se proporcionan
    today = datetime.utcnow().date()
    if not end_date_str:
        end_date = today
        end_date_str = end_date.isoformat()
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
            end_date_str = end_date.isoformat()
    
    if not start_date_str:
        start_date = end_date - timedelta(days=30)
        start_date_str = start_date.isoformat()
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = end_date - timedelta(days=30)
            start_date_str = start_date.isoformat()
    
    # Inicializar datos del informe
    report_data = {}
    
    try:
        if report_type == 'campaign':
            # Informe de campañas
            report_data = generate_campaign_report(start_date, end_date)
        elif report_type == 'job':
            # Informe de trabajos
            report_data = generate_job_report(start_date, end_date)
        elif report_type == 'candidate':
            # Informe de candidatos
            report_data = generate_candidate_report(start_date, end_date)
        else:
            # Tipo de informe no válido
            report_data = {'error': f"Tipo de informe no válido: {report_type}"}
    
    except Exception as e:
        current_app.logger.error(f"Error al generar informe: {e}", exc_info=True)
        report_data = {'error': f"Error al generar informe: {str(e)}"}
    
    return render_template('reports.html',
                           title="Informes",
                           report_type=report_type,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           report_data=report_data,
                           csrf_token_value=csrf_token_value)


@report_bp.route('/reports/export', methods=['POST'])
def export_report():
    """Exporta un informe a CSV."""
    # Obtener parámetros
    report_type = request.form.get('type', 'campaign')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    # Establecer fechas predeterminadas si no se proporcionan
    today = datetime.utcnow().date()
    if not end_date_str:
        end_date = today
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    
    if not start_date_str:
        start_date = end_date - timedelta(days=30)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = end_date - timedelta(days=30)
    
    try:
        # Generar datos del informe
        if report_type == 'campaign':
            report_data = generate_campaign_report(start_date, end_date)
            df = pd.DataFrame(report_data.get('campaigns', []))
        elif report_type == 'job':
            report_data = generate_job_report(start_date, end_date)
            df = pd.DataFrame(report_data.get('jobs', []))
        elif report_type == 'candidate':
            report_data = generate_candidate_report(start_date, end_date)
            df = pd.DataFrame(report_data.get('candidates', []))
        else:
            return jsonify({'error': f"Tipo de informe no válido: {report_type}"}), 400
        
        # Verificar si hay datos
        if df.empty:
            return jsonify({'error': 'No hay datos para exportar'}), 400
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Crear archivo en memoria para enviar
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        # Generar nombre de archivo
        filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        return send_file(
            mem,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        current_app.logger.error(f"Error al exportar informe: {e}", exc_info=True)
        return jsonify({'error': f"Error al exportar informe: {str(e)}"}), 500


def generate_campaign_report(start_date, end_date):
    """Genera un informe de campañas."""
    report_data = {
        'title': 'Informe de Campañas',
        'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        'campaigns': [],
        'summary': {},
        'charts': {}
    }
    
    try:
        # Consultar campañas
        campaigns = Campaign.query.options(db.joinedload(Campaign.job_opening)).all()
        
        # Consultar insights para el período
        insights = MetaInsight.query.filter(
            MetaInsight.date >= start_date,
            MetaInsight.date <= end_date
        ).all()
        
        # Agrupar insights por campaña
        insights_by_campaign = {}
        for insight in insights:
            if insight.campaign_id not in insights_by_campaign:
                insights_by_campaign[insight.campaign_id] = []
            insights_by_campaign[insight.campaign_id].append(insight)
        
        # Procesar cada campaña
        for campaign in campaigns:
            campaign_insights = insights_by_campaign.get(campaign.id, [])
            
            # Calcular métricas
            total_impressions = sum(insight.impressions for insight in campaign_insights)
            total_clicks = sum(insight.clicks for insight in campaign_insights)
            total_spend = sum(insight.spend for insight in campaign_insights)
            
            # Calcular métricas derivadas
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = total_spend / total_clicks if total_clicks > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            
            # Añadir datos de la campaña
            campaign_data = {
                'id': campaign.id,
                'name': campaign.name,
                'platform': campaign.platform,
                'status': campaign.status,
                'job_title': campaign.job_opening.title if campaign.job_opening else 'N/A',
                'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else 'N/A',
                'impressions': total_impressions,
                'clicks': total_clicks,
                'spend': total_spend,
                'ctr': round(ctr, 2),
                'cpc': round(cpc, 2),
                'cpm': round(cpm, 2)
            }
            
            report_data['campaigns'].append(campaign_data)
        
        # Ordenar campañas por impresiones (descendente)
        report_data['campaigns'].sort(key=lambda x: x['impressions'], reverse=True)
        
        # Calcular resumen
        total_campaigns = len(report_data['campaigns'])
        total_impressions = sum(c['impressions'] for c in report_data['campaigns'])
        total_clicks = sum(c['clicks'] for c in report_data['campaigns'])
        total_spend = sum(c['spend'] for c in report_data['campaigns'])
        
        report_data['summary'] = {
            'total_campaigns': total_campaigns,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_spend': total_spend,
            'avg_ctr': round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2),
            'avg_cpc': round(total_spend / total_clicks if total_clicks > 0 else 0, 2),
            'avg_cpm': round((total_spend / total_impressions * 1000) if total_impressions > 0 else 0, 2)
        }
        
        # Preparar datos para gráficos
        platform_counts = {}
        for campaign in report_data['campaigns']:
            platform = campaign['platform']
            if platform not in platform_counts:
                platform_counts[platform] = 0
            platform_counts[platform] += 1
        
        report_data['charts']['platform'] = {
            'labels': list(platform_counts.keys()),
            'data': list(platform_counts.values())
        }
        
        # Gráfico de impresiones por campaña (top 10)
        top_campaigns = sorted(report_data['campaigns'], key=lambda x: x['impressions'], reverse=True)[:10]
        report_data['charts']['impressions'] = {
            'labels': [c['name'] for c in top_campaigns],
            'data': [c['impressions'] for c in top_campaigns]
        }
        
        # Gráfico de clics por campaña (top 10)
        top_campaigns = sorted(report_data['campaigns'], key=lambda x: x['clicks'], reverse=True)[:10]
        report_data['charts']['clicks'] = {
            'labels': [c['name'] for c in top_campaigns],
            'data': [c['clicks'] for c in top_campaigns]
        }
    
    except Exception as e:
        current_app.logger.error(f"Error al generar informe de campañas: {e}", exc_info=True)
        report_data['error'] = f"Error al generar informe: {str(e)}"
    
    return report_data


def generate_job_report(start_date, end_date):
    """Genera un informe de trabajos."""
    report_data = {
        'title': 'Informe de Trabajos',
        'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        'jobs': [],
        'summary': {},
        'charts': {}
    }
    
    try:
        # Consultar trabajos
        jobs = JobOpening.query.all()
        
        # Procesar cada trabajo
        for job in jobs:
            # Contar campañas asociadas
            campaigns = Campaign.query.filter_by(job_opening_id=job.job_id).all()
            
            # Contar candidatos
            candidates = Candidate.query.filter_by(job_id=job.job_id).all()
            
            # Añadir datos del trabajo
            job_data = {
                'id': job.job_id,
                'title': job.title,
                'company': job.company_name,
                'location': job.location,
                'status': job.status,
                'created_at': job.created_at.strftime('%Y-%m-%d') if job.created_at else 'N/A',
                'campaign_count': len(campaigns),
                'candidate_count': len(candidates)
            }
            
            report_data['jobs'].append(job_data)
        
        # Ordenar trabajos por número de candidatos (descendente)
        report_data['jobs'].sort(key=lambda x: x['candidate_count'], reverse=True)
        
        # Calcular resumen
        total_jobs = len(report_data['jobs'])
        total_campaigns = sum(j['campaign_count'] for j in report_data['jobs'])
        total_candidates = sum(j['candidate_count'] for j in report_data['jobs'])
        
        report_data['summary'] = {
            'total_jobs': total_jobs,
            'total_campaigns': total_campaigns,
            'total_candidates': total_candidates,
            'avg_campaigns_per_job': round(total_campaigns / total_jobs if total_jobs > 0 else 0, 2),
            'avg_candidates_per_job': round(total_candidates / total_jobs if total_jobs > 0 else 0, 2)
        }
        
        # Preparar datos para gráficos
        status_counts = {}
        for job in report_data['jobs']:
            status = job['status']
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
        
        report_data['charts']['status'] = {
            'labels': list(status_counts.keys()),
            'data': list(status_counts.values())
        }
        
        # Gráfico de candidatos por trabajo (top 10)
        top_jobs = sorted(report_data['jobs'], key=lambda x: x['candidate_count'], reverse=True)[:10]
        report_data['charts']['candidates'] = {
            'labels': [j['title'] for j in top_jobs],
            'data': [j['candidate_count'] for j in top_jobs]
        }
    
    except Exception as e:
        current_app.logger.error(f"Error al generar informe de trabajos: {e}", exc_info=True)
        report_data['error'] = f"Error al generar informe: {str(e)}"
    
    return report_data


def generate_candidate_report(start_date, end_date):
    """Genera un informe de candidatos."""
    report_data = {
        'title': 'Informe de Candidatos',
        'period': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        'candidates': [],
        'summary': {},
        'charts': {}
    }
    
    try:
        # Consultar candidatos
        candidates = Candidate.query.options(db.joinedload(Candidate.job)).all()
        
        # Procesar cada candidato
        for candidate in candidates:
            # Añadir datos del candidato
            candidate_data = {
                'id': candidate.candidate_id,
                'name': candidate.name,
                'email': candidate.email,
                'location': candidate.location,
                'years_experience': candidate.years_experience,
                'education_level': candidate.education_level,
                'primary_skill': candidate.primary_skill,
                'job_title': candidate.job.title if candidate.job else 'N/A',
                'segment_id': candidate.segment_id
            }
            
            report_data['candidates'].append(candidate_data)
        
        # Ordenar candidatos por años de experiencia (descendente)
        report_data['candidates'].sort(key=lambda x: x['years_experience'] if x['years_experience'] is not None else 0, reverse=True)
        
        # Calcular resumen
        total_candidates = len(report_data['candidates'])
        avg_experience = sum(c['years_experience'] for c in report_data['candidates'] if c['years_experience'] is not None) / total_candidates if total_candidates > 0 else 0
        
        report_data['summary'] = {
            'total_candidates': total_candidates,
            'avg_experience': round(avg_experience, 2)
        }
        
        # Preparar datos para gráficos
        education_counts = {}
        for candidate in report_data['candidates']:
            education = candidate['education_level']
            if education not in education_counts:
                education_counts[education] = 0
            education_counts[education] += 1
        
        report_data['charts']['education'] = {
            'labels': list(education_counts.keys()),
            'data': list(education_counts.values())
        }
        
        # Gráfico de segmentos
        segment_counts = {}
        for candidate in report_data['candidates']:
            segment = f"Segmento {candidate['segment_id']}" if candidate['segment_id'] is not None else 'Sin segmentar'
            if segment not in segment_counts:
                segment_counts[segment] = 0
            segment_counts[segment] += 1
        
        report_data['charts']['segments'] = {
            'labels': list(segment_counts.keys()),
            'data': list(segment_counts.values())
        }
        
        # Gráfico de habilidades primarias (top 10)
        skill_counts = {}
        for candidate in report_data['candidates']:
            skill = candidate['primary_skill']
            if skill and skill not in skill_counts:
                skill_counts[skill] = 0
            if skill:
                skill_counts[skill] += 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        report_data['charts']['skills'] = {
            'labels': [s[0] for s in top_skills],
            'data': [s[1] for s in top_skills]
        }
    
    except Exception as e:
        current_app.logger.error(f"Error al generar informe de candidatos: {e}", exc_info=True)
        report_data['error'] = f"Error al generar informe: {str(e)}"
    
    return report_data
