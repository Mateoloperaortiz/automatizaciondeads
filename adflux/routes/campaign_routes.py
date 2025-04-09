"""
Rutas de campañas para AdFlux (Refactorizado para usar CampaignService).

Este módulo contiene las rutas relacionadas con la gestión de campañas publicitarias.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta

# Importar modelos solo si son estrictamente necesarios en la ruta (e.g., para poblar forms)
# La mayoría de interacciones con modelos ahora están en el servicio.
from ..models import JobOpening, Segment

from ..forms import CampaignForm
from ..constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLORS

# Importar el servicio
from ..services.campaign_service import CampaignService


# Instanciar el servicio (se podría inyectar dependencia si se usa un framework para ello)
campaign_service = CampaignService()

# Definir el blueprint
campaign_bp = Blueprint("campaign", __name__, template_folder="../templates")


@campaign_bp.route("/")
def list_campaigns():
    """Renderiza la página de lista de campañas usando CampaignService."""
    # Obtener parámetros de consulta para filtrado/ordenación
    platform_filter = request.args.get("platform")
    status_filter = request.args.get("status")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Podría venir de config

    try:
        # Obtener campañas paginadas desde el servicio
        pagination = campaign_service.get_campaigns_paginated(
            page=page,
            per_page=per_page,
            platform_filter=platform_filter,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        campaigns = pagination.items

        # Obtener estadísticas desde el servicio
        stats = campaign_service.get_campaign_stats()

        # Estandarizar los estados de las campañas para la vista
        for campaign in campaigns:
            # Convertir el estado a mayúsculas para buscar en el diccionario
            campaign.display_status = CAMPAIGN_STATUS.get(
                campaign.status.upper(), campaign.status.title() if campaign.status else "N/A"
            )
            campaign.status_color = CAMPAIGN_STATUS_COLORS.get(
                campaign.display_status, "bg-gray-100 text-gray-800"
            )

    except Exception as e:
        current_app.logger.error(f"Error al obtener lista de campañas: {e}", exc_info=True)
        flash("Error al cargar las campañas.", "error")
        pagination = None
        campaigns = []
        stats = {}

    # Generar token CSRF para formularios
    csrf_token_value = generate_csrf()

    return render_template(
        "campaigns_list.html",
        title="Campañas",
        campaigns=campaigns,
        stats=stats,
        platform_filter=platform_filter,
        status_filter=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        pagination=pagination,
        csrf_token_value=csrf_token_value,
        campaign_status=CAMPAIGN_STATUS, # Pasar constantes si se usan en la plantilla
        campaign_status_colors=CAMPAIGN_STATUS_COLORS # Pasar constantes si se usan en la plantilla
    )


@campaign_bp.route("/create", methods=["GET", "POST"])
def create_campaign():
    """Maneja la creación de una nueva campaña usando CampaignService."""
    form = CampaignForm()

    # Poblar opciones dinámicamente usando el servicio
    form.job_opening.choices = campaign_service.get_job_opening_choices()
    form.target_segment_ids.choices = campaign_service.get_segment_choices()

    # Preseleccionar segmento si se pasa por parámetro de consulta
    target_segment_id = request.args.get("target_segment_id", type=int)
    if (
        request.method == "GET"
        and target_segment_id
        and target_segment_id in [choice[0] for choice in form.target_segment_ids.choices]
    ):
        # WTForms espera una lista de strings para MultipleSelectField si las choices son int
        form.target_segment_ids.data = [str(target_segment_id)]


    # Pre-poblar job_opening si job_id está en los parámetros de consulta (petición GET)
    if request.method == "GET" and request.args.get("job_id"):
        job_id = request.args.get("job_id")
        # Usar el servicio para buscar el job
        job = campaign_service.get_job_opening_by_job_id(job_id)
        if job:
            form.job_opening.data = job_id # Pasar el ID al SelectField
        else:
            flash(f"El ID de puesto '{job_id}' proporcionado en la URL no se encontró.", "warning")


    if form.validate_on_submit():
        # Extraer datos del formulario y el archivo de imagen
        form_data = form.data.copy() # Copiar datos del formulario
        # El campo job_opening del formulario ahora contiene el job_id seleccionado
        form_data['job_opening'] = form.job_opening.data

        image_file = form.creative_image.data # Obtener el FileStorage

        # Llamar al servicio para crear la campaña
        new_campaign, success, error_message = campaign_service.create_campaign(form_data, image_file)

        if success:
            flash(f"Campaña '{new_campaign.name}' creada exitosamente.", "success")
            return redirect(url_for("campaign.list_campaigns"))
        else:
            flash(f"Error al crear la campaña: {error_message}", "error")
            # No es necesario hacer rollback aquí, el servicio ya lo hizo

    # Renderizar formulario (GET o POST con error de validación/servicio)
    return render_template("campaign_form.html", title="Crear Campaña", form=form, is_edit=False)


@campaign_bp.route("/<int:campaign_id>/edit", methods=["GET", "POST"])
def edit_campaign(campaign_id):
    """Maneja la edición de una campaña existente usando CampaignService."""
    campaign = campaign_service.get_campaign_by_id(campaign_id)
    if not campaign: # Servicio devuelve 404, pero como doble check
        flash("Campaña no encontrada.", "error")
        return redirect(url_for("campaign.list_campaigns"))

    form = CampaignForm(obj=campaign)

    # Poblar opciones dinámicamente usando el servicio
    form.job_opening.choices = campaign_service.get_job_opening_choices()
    form.target_segment_ids.choices = campaign_service.get_segment_choices()

    if request.method == "GET":
        # Convertir daily_budget de centavos a float para el formulario
        if campaign.daily_budget is not None:
            form.daily_budget.data = campaign.daily_budget / 100.0
        else:
             form.daily_budget.data = None # Asegurar que es None si no hay presupuesto

        # Establecer job_opening seleccionado (usando job_id)
        form.job_opening.data = campaign.job_opening_id

        # Establecer segmentos seleccionados (lista de strings de IDs)
        if campaign.target_segment_ids:
            form.target_segment_ids.data = [str(sid) for sid in campaign.target_segment_ids]
        else:
            form.target_segment_ids.data = [] # Asegurar que es lista vacía si no hay segmentos

    if form.validate_on_submit():
        form_data = form.data.copy()
        form_data['job_opening'] = form.job_opening.data # El ID del job

        image_file = form.creative_image.data

        updated_campaign, success, error_message = campaign_service.update_campaign(campaign_id, form_data, image_file)

        if success:
            flash(f"Campaña '{updated_campaign.name}' actualizada exitosamente.", "success")
            return redirect(url_for("campaign.view_campaign_details", campaign_id=updated_campaign.id))
        else:
            flash(f"Error al actualizar la campaña: {error_message}", "error")

    # Renderizar formulario (GET o POST con error de validación/servicio)
    return render_template(
        "campaign_form.html",
        title=f"Editar Campaña: {campaign.name}",
        form=form,
        campaign=campaign, # Pasar la campaña original por si es necesaria en la plantilla
        is_edit=True,
    )


@campaign_bp.route("/<int:campaign_id>/publish", methods=["POST"])
def publish_campaign(campaign_id):
    """Publica una campaña usando CampaignService."""
    simulate = request.form.get("simulate", "false").lower() == "true"

    campaign, success, message = campaign_service.trigger_publish_campaign(campaign_id, simulate)

    if success:
        flash(message, "info")
    elif campaign.status == "published": # Mensaje específico si ya estaba publicada
        flash(message, "warning")
    else:
        flash(f"Error al iniciar la publicación de '{campaign.name}': {message}", "error")

    return redirect(url_for("campaign.view_campaign_details", campaign_id=campaign_id))


@campaign_bp.route("/<int:campaign_id>/delete", methods=["POST"])
def delete_campaign(campaign_id):
    """Elimina una campaña usando CampaignService."""
    success, message = campaign_service.delete_campaign(campaign_id)

    if success:
        flash(message, "success")
    else:
        flash(f"Error al eliminar la campaña: {message}", "error")

    # Siempre redirigir a la lista después de intentar eliminar
    return redirect(url_for("campaign.list_campaigns"))


@campaign_bp.route("/<int:campaign_id>", endpoint="view_campaign_details")
def campaign_details(campaign_id):
    """Renderiza la página de detalles para una campaña usando CampaignService."""
    try:
        campaign, job = campaign_service.get_campaign_details_data(campaign_id)
        csrf_token_value = generate_csrf()
        return render_template(
            "campaign_detail.html",
            title=f"Campaña: {campaign.name}",
            campaign=campaign,
            job=job,
            csrf_token_value=csrf_token_value,
        )
    except Exception as e: # Captura el 404 del servicio u otros errores
         current_app.logger.error(f"Error al obtener detalles de campaña {campaign_id}: {e}", exc_info=True)
         flash("Error al cargar los detalles de la campaña.", "error")
         return redirect(url_for("campaign.list_campaigns"))


@campaign_bp.route("/reports/campaign/<int:campaign_id>", endpoint="campaign_performance_report")
def campaign_performance_report(campaign_id):
    """Muestra un informe de rendimiento usando CampaignService."""

    # --- Manejo del Rango de Fechas (se mantiene en la ruta, ya que es parte de la UI/request) ---
    default_end_date_dt = datetime.utcnow().date()
    default_start_date_dt = default_end_date_dt - timedelta(days=30)
    start_date_str = request.args.get("start_date", default_start_date_dt.isoformat())
    end_date_str = request.args.get("end_date", default_end_date_dt.isoformat())
    try:
        start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        start_date_dt = default_start_date_dt
        start_date_str = start_date_dt.isoformat()
        flash("Formato de fecha de inicio inválido, usando predeterminado.", "warning")
    try:
        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        end_date_dt = default_end_date_dt
        end_date_str = end_date_dt.isoformat()
        flash("Formato de fecha de fin inválido, usando predeterminado.", "warning")
    if start_date_dt > end_date_dt:
        start_date_dt = default_start_date_dt
        end_date_dt = default_end_date_dt
        start_date_str = start_date_dt.isoformat()
        end_date_str = end_date_dt.isoformat()
        flash(
            "La fecha de inicio no puede ser posterior a la fecha de fin, usando el rango predeterminado.",
            "warning",
        )
    # --------------------------

    try:
        # Obtener la campaña base (para mostrar título, etc.)
        campaign = campaign_service.get_campaign_by_id(campaign_id)

        # Obtener estadísticas de rendimiento desde el servicio
        stats = campaign_service.get_campaign_performance_report(campaign_id, start_date_dt, end_date_dt)

        return render_template(
            "campaign_performance.html",
            title=f"Rendimiento de Campaña: {campaign.name}",
            campaign=campaign,
            stats=stats,
            default_start_date=start_date_str,
            default_end_date=end_date_str,
        )

    except Exception as e: # Captura el 404 del servicio u otros errores
         current_app.logger.error(f"Error al generar informe de campaña {campaign_id}: {e}", exc_info=True)
         flash("Error al cargar el informe de rendimiento.", "error")
         # Redirigir a detalles o lista si falla el informe?
         return redirect(url_for("campaign.view_campaign_details", campaign_id=campaign_id))

# Eliminar funciones auxiliares que ahora están en el servicio
# def allowed_file(filename): ...
# def save_uploaded_image(file_storage): ...
