"""
Rutas de informes para AdFlux (Refactorizado para usar ReportService).

Este módulo contiene las rutas relacionadas con la generación de informes.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    jsonify,
    send_file,
    flash,
)
from datetime import datetime, timedelta
import pandas as pd
import io
from flask_wtf.csrf import generate_csrf

# Importar el servicio
from ..services.report_service import ReportService

# Instanciar el servicio
report_service = ReportService()

# Definir el blueprint
report_bp = Blueprint("report", __name__, template_folder="../templates")


# Helper para parsear y validar fechas
def _parse_date_range(start_date_str, end_date_str):
    today = datetime.utcnow().date()
    default_end_date = today
    default_start_date = default_end_date - timedelta(days=30)

    if not end_date_str:
        end_date = default_end_date
    else:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Formato de fecha de fin inválido, usando predeterminado.", "warning")
            end_date = default_end_date

    if not start_date_str:
        start_date = default_start_date
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Formato de fecha de inicio inválido, usando predeterminado.", "warning")
            start_date = default_start_date

    if start_date > end_date:
        flash(
            "La fecha de inicio no puede ser posterior a la fecha de fin, usando rango predeterminado.",
            "warning",
        )
        start_date = default_start_date
        end_date = default_end_date

    return start_date, end_date


@report_bp.route("/reports")
def reports_dashboard():
    """Renderiza la página principal de informes usando ReportService."""
    csrf_token_value = generate_csrf()

    report_type = request.args.get("type", "campaign")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date, end_date = _parse_date_range(start_date_str, end_date_str)

    report_data = {}
    try:
        if report_type == "campaign":
            report_data = report_service.generate_campaign_report(start_date, end_date)
        elif report_type == "job":
            report_data = report_service.generate_job_report(start_date, end_date)
        elif report_type == "candidate":
            report_data = report_service.generate_candidate_report(start_date, end_date)
        else:
            flash(f"Tipo de informe no válido: {report_type}", "warning")
            report_data = {"error": f"Tipo de informe no válido: {report_type}"}

        # Verificar si el servicio devolvió un error interno
        if report_data.get("error"):
            flash(report_data["error"], "error")

    except Exception as e:
        current_app.logger.error(f"Error en la ruta de informes: {e}", exc_info=True)
        flash("Ocurrió un error inesperado al generar el informe.", "error")
        report_data = {"error": "Error inesperado."}

    return render_template(
        "reports.html",
        title="Informes",
        report_type=report_type,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        report_data=report_data,
        csrf_token_value=csrf_token_value,
    )


@report_bp.route("/reports/export", methods=["POST"])
def export_report():
    """Exporta un informe a CSV usando ReportService."""
    report_type = request.form.get("type", "campaign")
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")

    start_date, end_date = _parse_date_range(start_date_str, end_date_str)

    try:
        # Obtener datos del servicio
        if report_type == "campaign":
            report_data = report_service.generate_campaign_report(start_date, end_date)
            data_key = "campaigns"
        elif report_type == "job":
            report_data = report_service.generate_job_report(start_date, end_date)
            data_key = "jobs"
        elif report_type == "candidate":
            report_data = report_service.generate_candidate_report(start_date, end_date)
            data_key = "candidates"
        else:
            return jsonify({"error": f"Tipo de informe no válido: {report_type}"}), 400

        # Verificar errores internos del servicio
        if report_data.get("error"):
            return jsonify({"error": report_data["error"]}), 500

        # Extraer los datos principales para el DataFrame
        data_list = report_data.get(data_key, [])
        if not data_list:
             # Usar flash y redirigir o devolver JSON?
             # Por consistencia con la UI, usar flash podría ser mejor,
             # pero la ruta es POST, así que jsonify es más estándar.
            return jsonify({"error": "No hay datos para exportar en el período seleccionado"}), 404 # 404 Not Found podría ser más apropiado que 400

        df = pd.DataFrame(data_list)

        # Crear archivo CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8') # Especificar encoding
        output.seek(0)

        mem = io.BytesIO()
        # Asegurarse de escribir bytes codificados correctamente
        mem.write(output.getvalue().encode("utf-8"))
        mem.seek(0)

        filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"

        return send_file(
            mem,
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error al exportar informe: {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado al exportar informe: {str(e)}"}), 500

# Las funciones generate_*_report ahora están en ReportService y se eliminan de aquí.
