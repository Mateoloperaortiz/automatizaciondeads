"""
Rutas principales para AdFlux.

Este módulo contiene las rutas principales de la aplicación que no pertenecen
a ninguna categoría específica.
"""

from flask import Blueprint, render_template, redirect, url_for, flash

# Definir el blueprint
main_bp = Blueprint("main", __name__, template_folder="../templates")


@main_bp.route("/")
def index():
    """Redirige a la página del panel de control."""
    return redirect(url_for("dashboard.index"))


@main_bp.route("/about")
def about():
    """Renderiza la página de información sobre la aplicación."""
    return render_template("about.html", title="Acerca de AdFlux")


@main_bp.route("/help")
def help_page():
    """Renderiza la página de ayuda."""
    return render_template("help.html", title="Ayuda")


@main_bp.route("/contact")
def contact():
    """Renderiza la página de contacto."""
    return render_template("contact.html", title="Contacto")


@main_bp.route("/privacy")
def privacy():
    """Renderiza la página de política de privacidad."""
    return render_template("privacy.html", title="Política de Privacidad")


@main_bp.route("/terms")
def terms():
    """Renderiza la página de términos y condiciones."""
    return render_template("terms.html", title="Términos y Condiciones")


@main_bp.route("/error")
def error():
    """Renderiza una página de error para pruebas."""
    # Generar un error para probar el manejo de errores
    try:
        1 / 0
    except Exception as e:
        flash(f"Error generado para pruebas: {e}", "error")

    return render_template("error.html", title="Error")
