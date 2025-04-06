"""
Rutas de campañas para AdFlux.

Este módulo contiene las rutas relacionadas con la gestión de campañas publicitarias.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from ..models import db, Campaign, JobOpening, Segment, MetaInsight, MetaAdSet
from ..forms import CampaignForm
from ..tasks import async_publish_adflux_campaign
from ..extensions import csrf
from flask_wtf.csrf import generate_csrf
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS

# Definir el blueprint
campaign_bp = Blueprint('campaign', __name__, template_folder='../templates')

# Constantes para la subida de archivos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file_storage):
    """Guarda una imagen subida y devuelve la ruta relativa."""
    if file_storage and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        # Construir ruta completa usando la configuración
        upload_path_relative = current_app.config.get('UPLOAD_FOLDER', 'adflux/static/uploads') # Obtener de config con fallback
        upload_path_absolute = os.path.join(current_app.root_path, '..', upload_path_relative)
        # Asegurar que el directorio de subida exista
        os.makedirs(upload_path_absolute, exist_ok=True)

        file_path = os.path.join(upload_path_absolute, filename)
        try:
            file_storage.save(file_path)
            # Devolver ruta relativa para guardar en BD
            return os.path.join(upload_path_relative, filename)
        except Exception as e:
            current_app.logger.error(f"Error al guardar archivo: {e}", exc_info=True)
            return None
    return None


@campaign_bp.route('/')
def list_campaigns():
    """Renderiza la página de lista de campañas."""
    # Obtener parámetros de consulta para filtrado/ordenación
    platform_filter = request.args.get('platform')
    status_filter = request.args.get('status')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # Consulta base
    query = Campaign.query.options(db.joinedload(Campaign.job_opening))

    # Aplicar filtros
    if platform_filter:
        query = query.filter(Campaign.platform == platform_filter)
    if status_filter:
        query = query.filter(Campaign.status == status_filter)

    # Aplicar ordenación
    if sort_by == 'name':
        sort_column = Campaign.name
    elif sort_by == 'platform':
        sort_column = Campaign.platform
    elif sort_by == 'status':
        sort_column = Campaign.status
    else:  # default to created_at
        sort_column = Campaign.created_at

    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Configuración de paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Ejecutar consulta con paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    campaigns = pagination.items

    # Obtener estadísticas para mostrar en la página
    stats = {}
    try:
        # Contar campañas por plataforma
        platform_counts = db.session.query(Campaign.platform, func.count(Campaign.id)).group_by(Campaign.platform).all()
        stats['platform_counts'] = dict(platform_counts)

        # Contar campañas por estado
        status_counts = db.session.query(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status).all()
        stats['status_counts'] = dict(status_counts)

        # Preparar datos para gráficos
        if platform_counts:
            platform_labels = [p for p, _ in platform_counts if p]
            platform_data = [c for _, c in platform_counts if _]
            stats['platform_chart'] = {'labels': platform_labels, 'data': platform_data}

        if status_counts:
            status_labels = [s for s, _ in status_counts if s]
            status_data = [c for _, c in status_counts if _]
            stats['status_chart'] = {'labels': status_labels, 'data': status_data}

    except Exception as e:
        current_app.logger.error(f"Error al generar estadísticas de campañas: {e}", exc_info=True)
        stats = {}

    # Estandarizar los estados de las campañas
    for campaign in campaigns:
        # Convertir el estado a mayúsculas para buscar en el diccionario
        campaign.display_status = CAMPAIGN_STATUS.get(campaign.status.upper(), campaign.status.title())
        campaign.status_color = CAMPAIGN_STATUS_COLORS.get(campaign.display_status, 'bg-gray-100 text-gray-800')

    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    return render_template('campaigns_list.html',
                           title="Campañas",
                           campaigns=campaigns,
                           stats=stats,
                           platform_filter=platform_filter,
                           status_filter=status_filter,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           pagination=pagination,
                           csrf_token_value=csrf_token_value,
                           campaign_status=CAMPAIGN_STATUS,
                           campaign_status_colors=CAMPAIGN_STATUS_COLORS)


@campaign_bp.route('/create', methods=['GET', 'POST'])
def create_campaign():
    """Maneja la creación de una nueva campaña de AdFlux."""
    form = CampaignForm()

    # Poblar opciones dinámicamente - Usar job_id
    form.job_opening.choices = [(jo.job_id, jo.title) for jo in JobOpening.query.order_by(JobOpening.title).all()]
    form.target_segment_ids.choices = [(s.id, s.name) for s in Segment.query.order_by(Segment.name).all()]

    # Preseleccionar segmento si se pasa por parámetro de consulta
    target_segment_id = request.args.get('target_segment_id', type=int)
    if request.method == 'GET' and target_segment_id and target_segment_id in [choice[0] for choice in form.target_segment_ids.choices]:
        form.target_segment_ids.data = [target_segment_id] # Establecer selección predeterminada

    # Pre-poblar job_opening si job_id está en los parámetros de consulta (petición GET)
    if request.method == 'GET' and request.args.get('job_id'):
        job_id = request.args.get('job_id')
        job = JobOpening.query.filter_by(job_id=job_id).first()
        if job:
            form.job_opening.data = job # Establecer el objeto preseleccionado
        else:
            flash(f"El ID de puesto '{job_id}' proporcionado en la URL no se encontró.", 'warning')

    if form.validate_on_submit():
        try:
            # Manejar subida de archivo
            saved_filename = None
            if form.creative_image.data:
                saved_filename = save_uploaded_image(form.creative_image.data)
                if not saved_filename:
                    flash('La subida de la imagen falló o el tipo de archivo no está permitido.', 'warning')
                    # Decidir si continuar sin imagen o detenerse

            daily_budget_cents = int(form.daily_budget.data * 100) if form.daily_budget.data else None

            new_campaign = Campaign(
                name=form.name.data,
                description=form.description.data,
                platform=form.platform.data,
                status=form.status.data,
                daily_budget=daily_budget_cents,
                job_opening=form.job_opening.data,
                target_segment_ids=form.target_segment_ids.data,
                primary_text=form.primary_text.data,
                headline=form.headline.data,
                link_description=form.link_description.data,
                creative_image_filename=saved_filename # Guardar el nombre de archivo
            )
            db.session.add(new_campaign)
            db.session.commit()

            flash(f"Campaña '{new_campaign.name}' creada exitosamente.", 'success')
            return redirect(url_for('campaign.list_campaigns'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la campaña: {e}", 'error')
            current_app.logger.error(f"Error al crear campaña: {e}", exc_info=True)

    return render_template('campaign_form.html',
                           title="Crear Campaña",
                           form=form,
                           is_edit=False)


# Esta ruta se ha movido y combinado con la ruta 'view_campaign_details' más abajo


@campaign_bp.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    """Maneja la edición de una campaña existente."""
    campaign = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm(obj=campaign)

    # Poblar opciones dinámicamente
    form.job_opening.choices = [(jo.job_id, jo.title) for jo in JobOpening.query.order_by(JobOpening.title).all()]
    form.target_segment_ids.choices = [(s.id, s.name) for s in Segment.query.order_by(Segment.name).all()]

    if request.method == 'GET':
        # Convertir daily_budget de centavos a dólares para el formulario
        if campaign.daily_budget:
            form.daily_budget.data = campaign.daily_budget / 100.0

        # Establecer segmentos seleccionados
        if campaign.target_segment_ids:
            form.target_segment_ids.data = campaign.target_segment_ids

    if form.validate_on_submit():
        try:
            # Manejar subida de archivo
            if form.creative_image.data:
                saved_filename = save_uploaded_image(form.creative_image.data)
                if saved_filename:
                    campaign.creative_image_filename = saved_filename
                else:
                    flash('La subida de la imagen falló o el tipo de archivo no está permitido.', 'warning')

            # Actualizar campos
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.platform = form.platform.data
            campaign.status = form.status.data
            campaign.daily_budget = int(form.daily_budget.data * 100) if form.daily_budget.data else None
            campaign.job_opening = form.job_opening.data
            campaign.target_segment_ids = form.target_segment_ids.data
            campaign.primary_text = form.primary_text.data
            campaign.headline = form.headline.data
            campaign.link_description = form.link_description.data

            db.session.commit()
            flash(f"Campaña '{campaign.name}' actualizada exitosamente.", 'success')
            return redirect(url_for('campaign.view_campaign_details', campaign_id=campaign.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la campaña: {e}", 'error')
            current_app.logger.error(f"Error al actualizar campaña {campaign_id}: {e}", exc_info=True)

    return render_template('campaign_form.html',
                           title=f"Editar Campaña: {campaign.name}",
                           form=form,
                           campaign=campaign,
                           is_edit=True)


@campaign_bp.route('/<int:campaign_id>/publish', methods=['POST'])
def publish_campaign(campaign_id):
    """Publica una campaña en la plataforma correspondiente."""
    campaign = Campaign.query.get_or_404(campaign_id)

    # Verificar si la campaña ya está publicada
    if campaign.status == 'published':
        flash(f"La campaña '{campaign.name}' ya está publicada.", 'warning')
        return redirect(url_for('campaign.view_campaign_details', campaign_id=campaign.id))

    try:
        # Iniciar tarea asíncrona para publicar la campaña
        simulate = request.form.get('simulate', 'false').lower() == 'true'
        task = async_publish_adflux_campaign.delay(campaign.id, simulate)

        # Actualizar estado de la campaña
        campaign.status = 'publishing'
        db.session.commit()

        flash(f"Publicación de campaña '{campaign.name}' iniciada. ID de tarea: {task.id}", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al iniciar la publicación de la campaña: {e}", 'error')
        current_app.logger.error(f"Error al publicar campaña {campaign_id}: {e}", exc_info=True)

    return redirect(url_for('campaign.view_campaign_details', campaign_id=campaign.id))


@campaign_bp.route('/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Elimina una campaña."""
    campaign = Campaign.query.get_or_404(campaign_id)

    try:
        name = campaign.name
        db.session.delete(campaign)
        db.session.commit()
        flash(f"Campaña '{name}' eliminada exitosamente.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la campaña: {e}", 'error')
        current_app.logger.error(f"Error al eliminar campaña {campaign_id}: {e}", exc_info=True)

    return redirect(url_for('campaign.list_campaigns'))


@campaign_bp.route('/<int:campaign_id>', endpoint='view_campaign_details')
def campaign_details(campaign_id):
    """Renderiza la página de detalles para una campaña AdFlux específica."""
    campaign = Campaign.query.get_or_404(campaign_id)

    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    # Obtener trabajo asociado
    job = None
    if campaign.job_opening_id:
        job = JobOpening.query.get(campaign.job_opening_id)

    return render_template('campaign_detail.html',
                           title=f"Campaña: {campaign.name}",
                           campaign=campaign,
                           job=job,
                           csrf_token_value=csrf_token_value)


@campaign_bp.route('/reports/campaign/<int:campaign_id>', endpoint='campaign_performance_report')
def campaign_performance_report(campaign_id):
    """Muestra un informe de rendimiento detallado para una campaña AdFlux específica."""
    campaign = Campaign.query.get_or_404(campaign_id)

    # --- Manejo del Rango de Fechas ---
    default_end_date_dt = datetime.utcnow().date()
    default_start_date_dt = default_end_date_dt - timedelta(days=30)
    start_date_str = request.args.get('start_date', default_start_date_dt.isoformat())
    end_date_str = request.args.get('end_date', default_end_date_dt.isoformat())
    try: start_date_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError: start_date_dt = default_start_date_dt; start_date_str = start_date_dt.isoformat(); flash("Formato de fecha de inicio inválido.", "warning")
    try: end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError: end_date_dt = default_end_date_dt; end_date_str = end_date_dt.isoformat(); flash("Formato de fecha de fin inválido.", "warning")
    if start_date_dt > end_date_dt:
        start_date_dt = default_start_date_dt; end_date_dt = default_end_date_dt
        start_date_str = start_date_dt.isoformat(); end_date_str = end_date_dt.isoformat()
        flash("La fecha de inicio no puede ser posterior a la fecha de fin, usando el rango predeterminado.", "warning")
    # --------------------------

    # --- Inicializar diccionario de estadísticas con valores predeterminados --- #
    stats = {
        'total_spend': 0.0, 'total_impressions': 0, 'total_clicks': 0,
        'ctr': 0.0, 'cpc': 0.0,
        # Marcadores de posición para gráficos/tablas
        'spend_over_time_chart': None,
        'ad_set_performance': []
    }
    # ------------------------------------------------- #

    # Obtener insights solo si la campaña ha sido publicada (tiene un ID externo)
    if campaign.external_campaign_id:
        try:
            # Consulta base para insights para ESTA campaña en el rango de fechas
            insights_base_query = MetaInsight.query.filter(
                MetaInsight.meta_campaign_id == campaign.external_campaign_id,
                MetaInsight.date_start >= start_date_dt,
                MetaInsight.date_stop <= end_date_dt
            )

            # Totales de Métricas de Rendimiento para esta Campaña
            performance_totals = insights_base_query.with_entities(
                func.sum(MetaInsight.spend),
                func.sum(MetaInsight.impressions),
                func.sum(MetaInsight.clicks)
            ).first()

            if performance_totals and performance_totals[0] is not None:
                stats['total_spend'] = float(performance_totals[0] or 0)
                stats['total_impressions'] = int(performance_totals[1] or 0)
                stats['total_clicks'] = int(performance_totals[2] or 0)

                # Calcular CTR y CPC
                if stats['total_impressions'] > 0:
                    stats['ctr'] = (stats['total_clicks'] / stats['total_impressions']) * 100
                if stats['total_clicks'] > 0:
                    stats['cpc'] = stats['total_spend'] / stats['total_clicks']

            # Datos para gráfico de gasto a lo largo del tiempo
            daily_spend = insights_base_query.with_entities(
                MetaInsight.date_start,
                func.sum(MetaInsight.spend)
            ).group_by(MetaInsight.date_start).order_by(MetaInsight.date_start).all()

            if daily_spend:
                stats['spend_over_time_chart'] = {
                    'labels': [day[0].strftime('%Y-%m-%d') for day in daily_spend],
                    'data': [float(day[1]) for day in daily_spend]
                }

            # Rendimiento por conjunto de anuncios
            if campaign.platform == 'meta':
                # Obtener todos los conjuntos de anuncios para esta campaña
                ad_sets = MetaAdSet.query.filter_by(meta_campaign_id=campaign.external_campaign_id).all()

                for ad_set in ad_sets:
                    # Obtener insights para este conjunto de anuncios
                    ad_set_insights = insights_base_query.filter(
                        MetaInsight.meta_ad_set_id == ad_set.ad_set_id
                    ).with_entities(
                        func.sum(MetaInsight.spend),
                        func.sum(MetaInsight.impressions),
                        func.sum(MetaInsight.clicks)
                    ).first()

                    if ad_set_insights and ad_set_insights[0] is not None:
                        ad_set_spend = float(ad_set_insights[0] or 0)
                        ad_set_impressions = int(ad_set_insights[1] or 0)
                        ad_set_clicks = int(ad_set_insights[2] or 0)

                        # Calcular CTR y CPC para este conjunto de anuncios
                        ad_set_ctr = 0
                        if ad_set_impressions > 0:
                            ad_set_ctr = (ad_set_clicks / ad_set_impressions) * 100

                        ad_set_cpc = 0
                        if ad_set_clicks > 0:
                            ad_set_cpc = ad_set_spend / ad_set_clicks

                        stats['ad_set_performance'].append({
                            'name': ad_set.name,
                            'id': ad_set.ad_set_id,
                            'spend': ad_set_spend,
                            'impressions': ad_set_impressions,
                            'clicks': ad_set_clicks,
                            'ctr': ad_set_ctr,
                            'cpc': ad_set_cpc
                        })

        except Exception as e:
            current_app.logger.error(f"Error al obtener insights para la campaña {campaign_id}: {e}", exc_info=True)
            flash(f"Error al obtener datos de rendimiento: {e}", 'error')

    return render_template('campaign_performance.html',
                           title=f"Rendimiento de Campaña: {campaign.name}",
                           campaign=campaign,
                           stats=stats,
                           default_start_date=start_date_str,
                           default_end_date=end_date_str)
