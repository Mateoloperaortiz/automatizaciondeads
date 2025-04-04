from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
# Importar modelos necesarios
from ..models import db, JobOpening, Candidate, Campaign, MetaInsight, MetaAdSet, Segment # Añadir Segment
# Importar el formulario
from ..forms import CampaignForm, SegmentForm # Importar SegmentForm
# Importar la función de análisis
from ..ml_model import analyze_segments_from_db
# Importar la función de prueba de Meta
from ..api_clients import test_meta_api_connection
# Importar la tarea de publicación
# ELIMINADO: from ..tasks import publish_adflux_campaign_to_meta, trigger_train_and_predict, run_candidate_segmentation_task
from ..tasks import trigger_train_and_predict, run_candidate_segmentation_task # Mantener otras importaciones de tareas
# Importar funciones para actualizar .env (usar una biblioteca como python-dotenv)
import os
from dotenv import set_key, find_dotenv # Necesario instalar python-dotenv si no está ya
from sqlalchemy import func, distinct, desc # Para contar y distinct
from flask import current_app # Añadido flash
from datetime import datetime, timedelta # Importar componentes datetime
from ..extensions import csrf # Importar extensión csrf
from flask_wtf.csrf import generate_csrf # Importar la función correcta
from werkzeug.utils import secure_filename
from sqlalchemy.sql import or_
from collections import Counter

# Definir el blueprint
main_bp = Blueprint('main', __name__, template_folder='../templates')

# Definir la ruta de la carpeta de subida (relativa a instance o static)
# ¡Asegúrate de que esta carpeta exista!
# UPLOAD_FOLDER = 'adflux/static/uploads' # Eliminar constante global

# Añadir una ruta para redirigir a la documentación de la API
@main_bp.route('/api-docs')
def api_docs():
    """Redirige a la documentación de la API"""
    return redirect('/api/docs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función auxiliar para guardar el archivo subido
def save_uploaded_image(file_storage):
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
            current_app.logger.info(f"Imagen guardada con éxito: {file_path}")
            return filename # Devolver el nombre de archivo guardado
        except Exception as e:
            current_app.logger.error(f"Error al guardar el archivo subido {filename}: {e}", exc_info=True)
            return None
    return None

@main_bp.route('/')
def index():
    """Redirige la URL raíz al dashboard."""
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    """Muestra el panel principal con estadísticas resumidas y gráficos."""
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

    stats = {
        # Recuentos
        'total_campaigns': 0, 'total_jobs': 0, 'total_candidates': 0,
        # Estado de la Campaña
        'status_counts': {}, 'status_chart_data': None,
        # Estado del Puesto
        'job_status_chart_data': None,
        # Segmentos de Candidatos
        'segment_chart_data': None,
        # Métricas de Rendimiento
        'total_spend': 0.0, 'total_impressions': 0, 'total_clicks': 0,
        'ctr': 0.0, 'cpc': 0.0,
        # Gráficos
        'spend_over_time_chart': None
    }
    try:
        # --- Recuentos (Sin filtro de fecha) ---
        stats['total_campaigns'] = db.session.query(func.count(Campaign.id)).scalar() or 0
        stats['total_jobs'] = db.session.query(func.count(JobOpening.job_id)).scalar() or 0
        stats['total_candidates'] = db.session.query(func.count(Candidate.candidate_id)).scalar() or 0

        # --- Estado y Gráfico de Campañas (Sin filtro de fecha) ---
        campaigns_by_status_query = db.session.query(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status).all()
        stats['status_counts'] = dict(campaigns_by_status_query)
        if campaigns_by_status_query:
            status_labels = [str(status).title() for status, count in campaigns_by_status_query if status is not None]
            status_data = [count for status, count in campaigns_by_status_query if status is not None]
            stats['status_chart_data'] = {'labels': status_labels, 'data': status_data}

        # --- Gráfico de Estado de Puestos (Sin filtro de fecha) ---
        job_status_counts = db.session.query(JobOpening.status, func.count(JobOpening.job_id)).group_by(JobOpening.status).all()
        if job_status_counts:
            job_labels = [str(status).title() for status, count in job_status_counts if status is not None]
            job_data = [count for status, count in job_status_counts if status is not None]
            stats['job_status_chart_data'] = {'labels': job_labels, 'data': job_data}

        # --- Gráfico de Segmentos de Candidatos (Sin filtro de fecha) ---
        segment_counts = db.session.query(Candidate.segment_id, func.count(Candidate.candidate_id)).group_by(Candidate.segment_id).order_by(Candidate.segment_id).all()
        if segment_counts:
            seg_labels = [f'Segmento {s}' if s is not None else 'Sin segmentar' for s, count in segment_counts]
            seg_data = [count for s, count in segment_counts]
            stats['segment_chart_data'] = {'labels': seg_labels, 'data': seg_data}

        # --- Consulta Base para Insights en Rango de Fechas ---
        insights_base_query = MetaInsight.query.filter(
            MetaInsight.date_start >= start_date_dt,
            MetaInsight.date_stop <= end_date_dt
        )

        # --- Totales de Métricas de Rendimiento ---
        performance_totals = insights_base_query.with_entities(
            func.sum(MetaInsight.spend),
            func.sum(MetaInsight.impressions),
            func.sum(MetaInsight.clicks)
        ).first()

        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        if performance_totals:
            total_spend = float(performance_totals[0]) if performance_totals[0] is not None else 0.0
            total_impressions = int(performance_totals[1]) if performance_totals[1] is not None else 0
            total_clicks = int(performance_totals[2]) if performance_totals[2] is not None else 0

        stats['total_spend'] = total_spend
        stats['total_impressions'] = total_impressions
        stats['total_clicks'] = total_clicks

        # --- Calcular Métricas Derivadas ---
        stats['ctr'] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
        stats['cpc'] = total_spend / total_clicks if total_clicks > 0 else 0.0

        # --- Datos del Gráfico de Gasto a lo Largo del Tiempo ---
        spend_over_time_data = insights_base_query.with_entities(
            MetaInsight.date_start,
            func.sum(MetaInsight.spend)
        ).group_by(
            MetaInsight.date_start
        ).order_by(
            MetaInsight.date_start
        ).all()

        if spend_over_time_data:
            sot_labels = [dt.strftime('%Y-%m-%d') for dt, spend in spend_over_time_data]
            sot_data = [float(spend) if spend is not None else 0.0 for dt, spend in spend_over_time_data]
            stats['spend_over_time_chart'] = {
                'labels': sot_labels,
                'data': sot_data
            }
        # ----------------------------------

    except Exception as e:
        current_app.logger.error(f"Error al obtener estadísticas del dashboard: {e}", exc_info=True)
        flash("No se pudieron cargar algunas estadísticas para el dashboard.", "error")
        # Mantener estadísticas predeterminadas

    return render_template('dashboard.html',
                           title='Dashboard',
                           stats=stats,
                           default_start_date=start_date_str,
                           default_end_date=end_date_str)

@main_bp.route('/campaigns')
def list_campaigns():
    """Lista todas las campañas."""
    page = request.args.get('page', 1, type=int)
    # Añadir filtrado/ordenación más tarde si es necesario
    campaigns_pagination = Campaign.query.order_by(Campaign.created_at.desc()).paginate(
        page=page, per_page=current_app.config.get('ITEMS_PER_PAGE', 10), error_out=False
    )
    campaigns = campaigns_pagination.items

    # Generar token CSRF para formularios de eliminación
    csrf_token_value = generate_csrf()

    return render_template('campaigns_list.html',
                           title="Campañas",
                           campaigns=campaigns,
                           pagination=campaigns_pagination,
                           csrf_token_value=csrf_token_value) # Pasar token

@main_bp.route('/campaigns/create', methods=['GET', 'POST'])
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
            flash(f'Campaña "{new_campaign.name}" creada con éxito!', 'success')
            return redirect(url_for('main.list_campaigns'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la campaña: {e}', 'error')

    return render_template('campaign_form.html',
                           title="Crear Nueva Campaña",
                           form=form,
                           form_action=url_for('main.create_campaign'))

@main_bp.route('/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    """Maneja la edición de una campaña AdFlux existente."""
    campaign = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm(obj=campaign)
    form.instance = campaign # Pasar instancia para acceso en plantilla

    # Poblar opciones dinámicamente aquí también - Usar job_id
    form.job_opening.choices = [(jo.job_id, jo.title) for jo in JobOpening.query.order_by(JobOpening.title).all()]
    form.target_segment_ids.choices = [(s.id, s.name) for s in Segment.query.order_by(Segment.name).all()]

    if request.method == 'GET':
        # Pre-poblar basado en el *job_id real* almacenado en la campaña
        # WTForms SelectField espera el *valor* (jo.job_id) para la preselección
        form.job_opening.data = campaign.job_opening_id
        form.target_segment_ids.data = campaign.target_segment_ids
        form.primary_text.data = campaign.primary_text
        form.headline.data = campaign.headline
        form.link_description.data = campaign.link_description
        form.daily_budget.data = campaign.daily_budget / 100.0 if campaign.daily_budget else None
        # Nota: FileField no se pre-pobla típicamente por razones de seguridad

    if form.validate_on_submit():
        try:
            saved_filename = campaign.creative_image_filename # Mantener existente si no hay nueva subida
            if form.creative_image.data:
                 # TODO: Opcionalmente eliminar archivo de imagen antiguo antes de guardar el nuevo
                new_filename = save_uploaded_image(form.creative_image.data)
                if new_filename:
                    saved_filename = new_filename
                else:
                    flash('La nueva subida de imagen falló o el tipo de archivo no está permitido. Manteniendo imagen existente (si existe).', 'warning')

            daily_budget_cents = int(form.daily_budget.data * 100) if form.daily_budget.data else None

            # Al poblar el objeto, WTForms maneja el mapeo del valor de SelectField de vuelta al objeto
            # Pero necesitamos asegurarnos de que la relación se maneje correctamente si no es automática
            selected_job_id = form.job_opening.data # Esto debería ser el job_id seleccionado (string)
            job_object = JobOpening.query.get(selected_job_id) # Obtener el objeto real

            # Actualizar campos de la campaña
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.platform = form.platform.data
            campaign.status = form.status.data
            campaign.job_opening = job_object # Asignar el objeto a la relación
            campaign.target_segment_ids = form.target_segment_ids.data
            campaign.primary_text = form.primary_text.data
            campaign.headline = form.headline.data
            campaign.link_description = form.link_description.data
            campaign.daily_budget = daily_budget_cents
            campaign.creative_image_filename = saved_filename # Actualizar nombre de archivo

            db.session.commit()
            flash(f'Campaña "{campaign.name}" actualizada con éxito!', 'success')
            return redirect(url_for('main.list_campaigns'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la campaña: {e}', 'error')

    return render_template('campaign_form.html',
                           title=f"Editar Campaña: {campaign.name}",
                           form=form,
                           form_action=url_for('main.edit_campaign', campaign_id=campaign.id))

@main_bp.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Elimina una campaña específica."""
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign_name = campaign.name # Obtener nombre antes de eliminar para mensaje flash
    try:
        # TODO: Añadir lógica aquí para eliminar recursos externos asociados si es necesario
        # ej., llamar a la API de Meta para eliminar campaign.external_campaign_id

        db.session.delete(campaign)
        db.session.commit()
        flash(f"Campaña '{campaign_name}' eliminada con éxito.", 'success')
        current_app.logger.info(f"Campaña eliminada ID {campaign_id} ('{campaign_name}')")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la campaña '{campaign_name}': {e}", 'error')
        current_app.logger.error(f"Error al eliminar la campaña ID {campaign_id} ('{campaign_name}'): {e}", exc_info=True)

    return redirect(url_for('main.list_campaigns')) # Redirigir de vuelta a la página de lista

@main_bp.route('/campaigns/<int:campaign_id>', endpoint='campaign_details')
def campaign_details(campaign_id):
    """Renderiza la página de detalles para una campaña AdFlux específica."""
    # Usar joinedload para cargar eficientemente la oferta de empleo relacionada
    campaign = Campaign.query.options(db.joinedload(Campaign.job_opening))\
                            .filter_by(id=campaign_id).first_or_404()

    return render_template('campaign_detail.html',
                           title=f"Campaña: {campaign.name}",
                           campaign=campaign)

@main_bp.route('/campaigns/<int:campaign_id>/publish', methods=['POST'])
def publish_campaign(campaign_id):
    """Maneja la publicación asíncrona de una campaña AdFlux a su plataforma."""
    campaign = Campaign.query.get_or_404(campaign_id)
    task = None
    simulate_publishing = True # Mantener el interruptor de simulación común por ahora

    try:
        if campaign.platform.lower() == 'meta':
            from ..tasks import async_publish_adflux_campaign_to_meta
            current_app.logger.info(f"Encolando tarea de publicación de Meta para campaña {campaign_id}")
            task = async_publish_adflux_campaign_to_meta.delay(campaign.id, simulate=simulate_publishing)

        elif campaign.platform.lower() == 'google':
            from ..tasks import async_publish_adflux_campaign_to_google
            current_app.logger.info(f"Encolando tarea de publicación de Google Ads para campaña {campaign_id}")
            # Asegurar que el argumento simulate coincida si es necesario, el predeterminado es True en la tarea
            task = async_publish_adflux_campaign_to_google.delay(campaign.id, simulate=simulate_publishing)

        else:
            # Plataforma aún no soportada
            flash(f"Publicación aún no implementada para la plataforma: {campaign.platform}", 'warning')
            return redirect(url_for('main.campaign_details', campaign_id=campaign.id))

        # Si una tarea fue encolada con éxito
        if task:
            flash(f"Proceso de publicación para la campaña '{campaign.name}' ({campaign.platform.title()}) iniciado en segundo plano (ID de Tarea: {task.id}).", 'info')
        else:
            # Este caso idealmente no debería alcanzarse si la verificación de plataforma es exhaustiva
            # pero sirve como fallback si .delay() falló silenciosamente antes de la excepción
             flash(f"No se pudo encolar la tarea de publicación para la plataforma '{campaign.platform}'.", 'error')

    except Exception as e:
        current_app.logger.error(f"Error al enviar la tarea de publicación para la campaña {campaign.id} (Plataforma: {campaign.platform}): {e}", exc_info=True)
        flash("Error al iniciar el proceso de publicación. Por favor, revise los registros del sistema.", 'error')

    # Redirigir inmediatamente, la tarea se ejecuta en segundo plano
    return redirect(url_for('main.campaign_details', campaign_id=campaign.id))

@main_bp.route('/jobs')
def list_jobs():
    """Renderiza la página de lista de empleos."""
    try:
        # Obtener empleos de la BD, ordenar por fecha de publicación más reciente
        jobs = JobOpening.query.order_by(JobOpening.posted_date.desc()).all()
    except Exception as e:
        flash(f"Error al obtener empleos: {e}", 'error')
        jobs = [] # Asegurar que jobs sea siempre una lista
    return render_template('jobs_list.html', title="Ofertas de Empleo", jobs=jobs)

@main_bp.route('/jobs/<string:job_id>')
def job_details(job_id):
    """Renderiza la página de detalles para una oferta de empleo específica."""
    job = JobOpening.query.filter_by(job_id=job_id).first_or_404()
    return render_template('job_detail.html', title=f"Empleo: {job.title}", job=job)

@main_bp.route('/candidates')
def list_candidates():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    segment_filter = request.args.get('segment') # Obtener filtro de segmento

    # Consulta base
    candidate_query = Candidate.query

    # Filtrado por segmento
    if segment_filter is not None:
        if segment_filter.lower() == 'none': # Manejar valor especial 'none' para no segmentados
            # Usar segment_id
            candidate_query = candidate_query.filter(Candidate.segment_id.is_(None))
        else:
            try:
                segment_id = int(segment_filter)
                # Usar segment_id
                candidate_query = candidate_query.filter(Candidate.segment_id == segment_id)
            except ValueError:
                flash(f"Valor de filtro de segmento inválido: {segment_filter}", "warning")
                # Opcionalmente ignorar filtro o redirigir

    # Funcionalidad de búsqueda (ejemplo simple en nombre y habilidad principal)
    if query:
        search_term = f"%{query}%"
        candidate_query = candidate_query.filter(
            or_(Candidate.name.ilike(search_term), Candidate.primary_skill.ilike(search_term))
        )

    # Lógica de ordenación
    # Usar segment_id para clave de ordenación
    sort_column = getattr(Candidate, sort_by if sort_by != 'segment' else 'segment_id', Candidate.name)
    if sort_order == 'desc':
        candidate_query = candidate_query.order_by(sort_column.desc())
    else:
        candidate_query = candidate_query.order_by(sort_column.asc())

    # Paginación
    pagination = candidate_query.paginate(page=page, per_page=current_app.config.get('ITEMS_PER_PAGE', 15), error_out=False)
    candidates = pagination.items

    # Preparar enlaces de ordenación (añadir filtro de segmento a los enlaces)
    sort_links = {}
    # Usar segment_id en la lista de columnas ordenables
    for col in ['name', 'primary_skill', 'years_experience', 'segment_id']:
        current_order = 'asc'
        if sort_by == col:
             # Manejar mapeo de vuelta a 'segment' si es lo que usa la URL por simplicidad
             effective_sort_by = 'segment' if col == 'segment_id' else col
             if effective_sort_by == sort_by and sort_order == 'asc':
                 current_order = 'desc'
        # Asegurar que el enlace use 'segment_id' si se ordena por él
        sort_links[col] = url_for('main.list_candidates', page=page, query=query, sort_by=col, sort_order=current_order, segment=segment_filter)

    # Necesitamos segment_map para la plantilla
    segments = Segment.query.all()
    segment_map = {s.id: s.name for s in segments}

    return render_template('candidates_list.html',
                           title='Candidatos',
                           candidates=candidates,
                           pagination=pagination,
                           query=query,
                           sort_links=sort_links,
                           current_sort_by=sort_by,
                           current_sort_order=sort_order,
                           segment_map=segment_map, # Pasar mapa de nuevo
                           current_segment_filter=segment_filter)

@main_bp.route('/candidates/<string:candidate_id>')
def candidate_detail(candidate_id):
    """Renderiza la página de detalle del candidato."""
    try:
        candidate = Candidate.query.filter_by(candidate_id=candidate_id).first_or_404()
    except Exception as e:
        flash(f"Error al obtener el candidato {candidate_id}: {e}", 'error')
        return redirect(url_for('main.list_candidates'))

    return render_template('candidate_detail.html',
                           title=f"Candidato: {candidate.name}",
                           candidate=candidate,
                           segment_map=SEGMENT_MAP) # Pasar el mapa

@main_bp.route('/segmentation')
def segmentation_analysis():
    """Muestra un análisis de los segmentos de candidatos."""
    csrf_token_value = generate_csrf()
    try:
        # Eliminar joinedload - obtener segmentos directamente
        segments = Segment.query.order_by(Segment.id).all()

        # Obtener todas las campañas y construir un mapa de segment_id -> [campañas que lo apuntan]
        all_campaigns = Campaign.query.all()
        campaigns_by_segment_id = {}
        for camp in all_campaigns:
            if isinstance(camp.target_segment_ids, list): # Verificar si es una lista
                for target_id in camp.target_segment_ids:
                    if target_id not in campaigns_by_segment_id:
                        campaigns_by_segment_id[target_id] = []
                    # Almacenar información limitada para evitar objetos grandes en el contexto
                    campaigns_by_segment_id[target_id].append({'id': camp.id, 'name': camp.name})

        # Pre-obtener datos de candidatos (código existente)
        all_candidates_data = db.session.query(
            Candidate.segment_id,
            Candidate.years_experience,
            Candidate.primary_skill,
            Candidate.location,
            Candidate.education_level
        ).all()
        candidates_by_segment = {}
        for data in all_candidates_data:
            seg_id = data.segment_id
            if seg_id not in candidates_by_segment:
                candidates_by_segment[seg_id] = []
            candidates_by_segment[seg_id].append(data)

        chart_labels = []
        chart_data_values = []
        segment_summary = []
        summary_stats = {
            'total_candidates': 0,
            'segmented_candidates': 0,
            'num_segments': 0
        }
        num_defined_segments_found = 0
        unsegmented_count = len(candidates_by_segment.get(None, []))
        has_unsegmented = unsegmented_count > 0

        # Procesar segmentos conocidos de la BD
        for segment in segments:
            seg_id = segment.id
            segment_candidates = candidates_by_segment.get(seg_id, [])
            count = len(segment_candidates)

            # Calcular estadísticas (código existente)
            avg_exp = 0
            top_skills = []
            top_locations = []
            edu_counts = {}
            if count > 0:
                total_exp = sum(c.years_experience for c in segment_candidates if c.years_experience is not None)
                exp_count = sum(1 for c in segment_candidates if c.years_experience is not None)
                avg_exp = total_exp / exp_count if exp_count > 0 else 0
                skill_counts = Counter(c.primary_skill for c in segment_candidates if c.primary_skill)
                top_skills = skill_counts.most_common(3)
                location_counts = Counter(c.location for c in segment_candidates if c.location)
                top_locations = location_counts.most_common(3)
                edu_counts = Counter(c.education_level for c in segment_candidates if c.education_level)

            chart_labels.append(segment.name)
            chart_data_values.append(count)
            if count > 0:
                num_defined_segments_found += 1
            summary_stats['total_candidates'] += count
            summary_stats['segmented_candidates'] += count

            # Obtener campañas asociadas del mapa que construimos
            associated_campaigns = campaigns_by_segment_id.get(seg_id, [])
            total_campaign_count = len(associated_campaigns)
            # Limitar campañas mostradas (se puede hacer aquí o en la plantilla)
            displayed_campaigns = associated_campaigns[:3]

            segment_summary.append({
                'id': seg_id,
                'name': segment.name,
                'description': segment.description,
                'count': count,
                'view_url': url_for('main.list_candidates', segment=seg_id),
                'avg_experience': avg_exp,
                'top_skills': top_skills,
                'top_locations': top_locations,
                'education_distribution': dict(edu_counts),
                'associated_campaigns': displayed_campaigns, # Usar la lista obtenida
                'total_campaign_count': total_campaign_count # Usar el recuento obtenido
            })

        # Añadir no segmentados (código existente)
        if has_unsegmented:
             segment_name = "Sin segmentar"
             chart_labels.append(segment_name)
             chart_data_values.append(unsegmented_count)
             summary_stats['total_candidates'] += unsegmented_count
             segment_summary.append({
                'id': None,
                'name': segment_name,
                'description': 'Candidatos no asignados a ningún segmento.',
                'count': unsegmented_count,
                'view_url': url_for('main.list_candidates', segment='none'),
                'avg_experience': None,
                'top_skills': [],
                'top_locations': [],
                'education_distribution': {},
                'associated_campaigns': [], # Sin campañas para no segmentados
                'total_campaign_count': 0
             })

        summary_stats['num_segments'] = num_defined_segments_found

        chart_data = {
            'labels': chart_labels,
            'data': chart_data_values
        } if chart_labels else None

    except Exception as e:
        current_app.logger.error(f"Error durante el análisis de segmentos: {e}", exc_info=True)
        flash("Error al generar el análisis de segmentación.", "error")
        chart_data = None
        segment_summary = []
        summary_stats = {}
        csrf_token_value = generate_csrf() # Regenerar en caso de error si es necesario

    return render_template('segmentation.html',
                           title="Análisis de Segmentación de Candidatos",
                           chart_data=chart_data,
                           segment_summary=segment_summary,
                           summary_stats=summary_stats,
                           csrf_token_value=csrf_token_value)

@main_bp.route('/segmentation/run', methods=['POST'])
def run_segmentation_task():
    """Dispara la tarea de segmentación ML."""
    try:
        # Usar la tarea Celery en lugar de la función directa
        task = run_candidate_segmentation_task.delay()
        flash(f"Tarea de segmentación iniciada. Los resultados se actualizarán en breve.", 'success')
    except Exception as e:
        current_app.logger.error(f"Error al disparar la tarea de segmentación: {e}", exc_info=True)
        flash("Ocurrió un error inesperado al intentar iniciar la tarea de segmentación.", 'error')

    return redirect(url_for('main.segmentation_analysis'))

@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Renderiza la página de configuración y conexiones y maneja las actualizaciones."""
    # Usar la config de Flask que incluye variables de entorno
    from flask import current_app

    test_result_message = None
    test_result_success = None

    # --- Generar token CSRF --- #
    csrf_token_value = generate_csrf()
    # -------------------------- #

    if request.method == 'POST':
        action = request.form.get('action')
        platform = request.form.get('platform')

        if platform == 'meta':
            account_id = request.form.get('meta_ad_account_id')
            access_token = request.form.get('meta_access_token')

            if action == 'save_meta':
                # --- Guardar Configuración de Meta en .env --- #
                dotenv_path = None # Inicializar
                try:
                    # Encontrar el archivo .env
                    dotenv_path = find_dotenv(raise_error_if_not_found=False, usecwd=True) # Buscar en CWD
                    if not dotenv_path:
                         # Intentar crearlo relativo a la ruta instance o raíz del proyecto
                         # Esto es complicado y podría depender de la estructura de tu proyecto
                         # Por simplicidad, asumamos que debe existir por ahora.
                         flash("Archivo .env no encontrado en la raíz del proyecto. No se puede guardar la configuración.", 'error')
                    else:
                        current_app.logger.info(f"Intentando actualizar claves en el archivo .env: {dotenv_path}")
                        # Usar cadena vacía si el campo del formulario falta o está vacío
                        account_id_to_save = account_id if account_id else ''
                        access_token_to_save = access_token if access_token else ''

                        # Escribir las claves
                        key_updated_1 = set_key(dotenv_path, "META_AD_ACCOUNT_ID", account_id_to_save)
                        key_updated_2 = set_key(dotenv_path, "META_ACCESS_TOKEN", access_token_to_save)

                        if key_updated_1 and key_updated_2:
                            flash("Configuración de Meta guardada en el archivo .env. Por favor REINICIE la aplicación para que los cambios surtan efecto completo.", 'success')
                        else:
                            # Esto podría indicar un problema de escritura de archivo incluso sin excepción
                             flash("Configuración guardada parcialmente o archivo sin cambios. Verifique los permisos del archivo y el contenido.", 'warning')
                        current_app.logger.info(f"Actualización del archivo .env finalizada: {dotenv_path}")

                except IOError as e:
                     current_app.logger.error(f"IOError al escribir en el archivo .env ({dotenv_path}): {e}")
                     flash(f"Error al guardar la configuración: No se pudo escribir en el archivo .env. Verifique los permisos.", 'error')
                except Exception as e:
                    current_app.logger.error(f"Error inesperado al guardar en el archivo .env ({dotenv_path}): {e}", exc_info=True)
                    flash(f"Error al guardar la configuración: {e}", 'error')
                # --- Fin Lógica de Guardado ---

            elif action == 'test_meta':
                if not account_id or not access_token:
                    flash("Se requieren tanto el ID de la cuenta publicitaria como el token de acceso para probar la conexión.", 'warning')
                else:
                    flash("Probando conexión con la API de Meta...", 'info')
                    success, message = test_meta_api_connection(account_id, access_token)
                    if success:
                        flash(message, 'success')
                        test_result_success = True
                    else:
                        flash(message, 'error')
                        test_result_success = False
                    test_result_message = message # Almacenar para mostrar

        elif platform == 'gemini':
            api_key = request.form.get('gemini_api_key')
            selected_model = request.form.get('gemini_model')
            available_models = []

            if action == 'save_gemini':
                # --- Guardar Configuración de Gemini en .env --- #
                dotenv_path = None # Inicializar
                try:
                    dotenv_path = find_dotenv(raise_error_if_not_found=False, usecwd=True)
                    if not dotenv_path:
                         flash("Archivo .env no encontrado en la raíz del proyecto. No se puede guardar la configuración.", 'error')
                    else:
                        current_app.logger.info(f"Intentando actualizar la configuración de Gemini en el archivo .env: {dotenv_path}")
                        # Quitar comillas de los valores
                        api_key_to_save = api_key.strip("'").strip('"') if api_key else ''
                        model_to_save = selected_model.strip("'").strip('"') if selected_model else ''

                        # Guardar tanto la clave API como el modelo seleccionado
                        key_updated = set_key(dotenv_path, "GEMINI_API_KEY", api_key_to_save, quote_mode="never")
                        model_updated = set_key(dotenv_path, "GEMINI_MODEL", model_to_save, quote_mode="never")

                        if key_updated and model_updated:
                            flash("Configuración de Gemini guardada en el archivo .env. Por favor REINICIE la aplicación para que los cambios surtan efecto completo.", 'success')
                        else:
                             flash("Configuración guardada parcialmente o archivo sin cambios. Verifique los permisos del archivo y el contenido.", 'warning')
                        current_app.logger.info(f"Actualización de la configuración de Gemini en el archivo .env finalizada: {dotenv_path}")

                except IOError as e:
                     current_app.logger.error(f"IOError al escribir en el archivo .env ({dotenv_path}): {e}")
                     flash(f"Error al guardar la configuración: No se pudo escribir en el archivo .env. Verifique los permisos.", 'error')
                except Exception as e:
                    current_app.logger.error(f"Error inesperado al guardar en el archivo .env ({dotenv_path}): {e}", exc_info=True)
                    flash(f"Error al guardar la configuración: {e}", 'error')
                # --- Fin Lógica de Guardado ---

            elif action == 'test_gemini':
                if not api_key:
                    flash("Se requiere la clave API para probar la conexión.", 'warning')
                else:
                    flash("Probando conexión con la API de Gemini...", 'info')
                    # Importar las funciones donde se necesiten
                    from ..api_clients import test_gemini_api_connection, get_available_gemini_models
                    success, message, models = get_available_gemini_models(api_key)
                    available_models = models  # Almacenar para la plantilla
                    if success:
                        flash(message, 'success')
                        test_result_success = True
                    else:
                        flash(message, 'error')
                        test_result_success = False
                    test_result_message = message

        # Re-renderizar la página para mostrar mensajes flash y posible actualización de estado
        return render_template('settings.html',
                               title="Configuración y Conexiones",
                               config=current_app.config,
                               form_values=request.form,
                               test_result_success=test_result_success,
                               test_result_message=test_result_message,
                               available_models=available_models,  # Pasar modelos a la plantilla
                               csrf_token_value=csrf_token_value)

    # Petición GET: solo renderizar la página
    # Para peticiones GET, intentar obtener modelos disponibles si existe la clave API
    available_models = []
    api_key = current_app.config.get('GEMINI_API_KEY')
    if api_key:
        from ..api_clients import get_available_gemini_models
        success, _, models = get_available_gemini_models(api_key)
        if success:
            available_models = models

    return render_template('settings.html',
                           title="Configuración y Conexiones",
                           config=current_app.config,
                           available_models=available_models,
                           csrf_token_value=csrf_token_value)

# --- Rutas de Informes --- #

@main_bp.route('/reports/campaign/<int:campaign_id>')
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

            total_spend = 0.0
            total_impressions = 0
            total_clicks = 0
            if performance_totals:
                total_spend = float(performance_totals[0]) if performance_totals[0] is not None else 0.0
                total_impressions = int(performance_totals[1]) if performance_totals[1] is not None else 0
                total_clicks = int(performance_totals[2]) if performance_totals[2] is not None else 0

            stats['total_spend'] = total_spend
            stats['total_impressions'] = total_impressions
            stats['total_clicks'] = total_clicks

            # Calcular Métricas Derivadas
            stats['ctr'] = (total_clicks / total_impressions) * 100.0 if total_impressions > 0 else 0.0
            stats['cpc'] = total_spend / total_clicks if total_clicks > 0 else 0.0

            # --- Obtener datos del gráfico de gasto a lo largo del tiempo --- #
            spend_over_time = insights_base_query.with_entities(
                # Asegurar que la fecha se convierta a cadena para etiquetado consistente
                func.cast(MetaInsight.date_start, db.String),
                func.sum(MetaInsight.spend)
            ).group_by(MetaInsight.date_start).order_by(MetaInsight.date_start).all()

            if spend_over_time:
                labels = [row[0] for row in spend_over_time]
                data = [float(row[1]) if row[1] is not None else 0.0 for row in spend_over_time]
                stats['spend_over_time_chart'] = {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Gasto Diario ($)',
                        'data': data,
                        'fill': False,
                        'borderColor': 'rgb(75, 192, 192)',
                        'tension': 0.1
                    }]
                }
            else:
                 stats['spend_over_time_chart'] = None # Asegurar None si no hay datos
            # -------------------------------------------- #

            # --- Obtener datos de rendimiento a nivel de conjunto de anuncios --- #
            # Unir MetaInsight con MetaAdSet para obtener el nombre
            ad_set_data = insights_base_query.join(
                MetaAdSet, MetaInsight.meta_ad_set_id == MetaAdSet.id
            ).with_entities(
                MetaInsight.meta_ad_set_id,
                MetaAdSet.name, # Seleccionar nombre de la tabla MetaAdSet
                func.sum(MetaInsight.spend),
                func.sum(MetaInsight.impressions),
                func.sum(MetaInsight.clicks)
            ).group_by(MetaInsight.meta_ad_set_id, MetaAdSet.name).all()

            ad_set_list = []
            for row in ad_set_data:
                ad_set_id, ad_set_name, spend, impressions, clicks = row
                spend = float(spend) if spend is not None else 0.0
                impressions = int(impressions) if impressions is not None else 0
                clicks = int(clicks) if clicks is not None else 0
                ctr = (clicks / impressions) * 100.0 if impressions > 0 else 0.0
                cpc = spend / clicks if clicks > 0 else 0.0
                ad_set_list.append({
                    'id': ad_set_id,
                    'name': ad_set_name or f"Conjunto Anuncios ID {ad_set_id}", # Usar nombre si está disponible
                    'spend': spend,
                    'impressions': impressions,
                    'clicks': clicks,
                    'ctr': ctr,
                    'cpc': cpc
                })
            stats['ad_set_performance'] = ad_set_list
            # ------------------------------------------ #

        except Exception as e:
            current_app.logger.error(f"Error al obtener insights para la campaña {campaign_id}: {e}", exc_info=True)
            flash(f"No se pudieron cargar las estadísticas de rendimiento para la campaña {campaign.name}.", "error")
            # Mantener estadísticas predeterminadas (ya inicializadas)

    else:
        flash(f"La campaña '{campaign.name}' aún no ha sido publicada. No hay datos de rendimiento disponibles.", "warning")

    # --- Registrar estadísticas antes de renderizar --- #
    current_app.logger.debug(f"Renderizando informe de campaña {campaign_id} con estadísticas: {stats}")
    # ---------------------------------- #

    return render_template('campaign_performance.html',
                           title=f"Informe: {campaign.name}",
                           campaign=campaign,
                           stats=stats,
                           default_start_date=start_date_str,
                           default_end_date=end_date_str)

@main_bp.route('/api/generate-ad-creative', methods=['POST'])
@csrf.exempt
def generate_ad_creative():
    """Endpoint API para generar texto creativo de anuncio usando Gemini."""
    try:
        # Obtener detalles del trabajo desde la solicitud
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos',
                'content': {}
            }), 400

        job_title = data.get('job_title')
        job_description = data.get('job_description')
        target_audience = data.get('target_audience', 'buscadores de empleo generales')

        if not job_title or not job_description:
            return jsonify({
                'success': False,
                'message': 'Se requieren título y descripción del trabajo',
                'content': {}
            }), 400

        # Importar la función de generación
        from ..api_clients import generate_ad_creative_gemini

        # Generar el creativo del anuncio
        success, message, content = generate_ad_creative_gemini(
            job_title=job_title,
            job_description=job_description,
            target_audience=target_audience
        )

        return jsonify({
            'success': success,
            'message': message,
            'content': content
        }), 200 if success else 500

    except Exception as e:
        current_app.logger.error(f"Error en el endpoint generate_ad_creative: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error del servidor: {str(e)}",
            'content': {}
        }), 500

@main_bp.route('/segmentation/<int:segment_id>/edit', methods=['GET', 'POST'])
def edit_segment(segment_id):
    """Maneja la edición de un Segmento existente.
    Nota: Generalmente no se recomienda editar el ID mismo.
    """
    segment = Segment.query.get_or_404(segment_id)
    form = SegmentForm(obj=segment) # Pre-poblar formulario con datos existentes

    if form.validate_on_submit():
        try:
            segment.name = form.name.data
            segment.description = form.description.data
            db.session.commit()
            flash(f"Segmento '{segment.name}' actualizado con éxito.", 'success')
            return redirect(url_for('main.segmentation_analysis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el segmento: {e}", 'error')
            current_app.logger.error(f"Error al actualizar el segmento {segment_id}: {e}", exc_info=True)

    return render_template('segment_edit.html',
                           title=f"Editar Segmento: {segment.name}",
                           form=form,
                           segment=segment)

@main_bp.route('/segmentation/trigger', methods=['POST'])
def trigger_segmentation():
    """Dispara la tarea en segundo plano para re-ejecutar la segmentación de candidatos."""
    try:
        task = run_candidate_segmentation_task.delay()
        flash(f"Tarea de segmentación de candidatos iniciada (ID de Tarea: {task.id}). Los resultados se actualizarán en breve.", 'info')
    except Exception as e:
        flash(f"Error al iniciar la tarea de segmentación: {e}", 'error')
        current_app.logger.error(f"Error al despachar la tarea de segmentación: {e}", exc_info=True)

    return redirect(url_for('main.segmentation_analysis'))

# Añadir rutas para CRUD de campañas, detalles de trabajo/candidato más tarde