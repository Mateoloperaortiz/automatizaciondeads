"""
Comandos CLI de operaciones de datos para AdFlux.

Este módulo contiene comandos para crear, sembrar y gestionar datos en la base de datos.
"""

import click
import os
from dotenv import load_dotenv
import json
import datetime
import re
from flask import current_app
from flask.cli import with_appcontext

from ..simulation import generate_multiple_jobs, generate_multiple_candidates
from ..models import JobOpening, Candidate
from ..extensions import db

# Crear grupo de comandos
data_ops_group = click.Group(
    name="data_ops", help="Comandos personalizados de operaciones de datos (crear, sembrar)."
)


@data_ops_group.command("create")
@with_appcontext
def db_create():
    """Crea las tablas de la base de datos basadas en models.py."""
    with current_app.app_context():
        try:
            db.create_all()
            click.echo("Tablas de base de datos creadas correctamente.")
        except Exception as e:
            click.echo(f"Error creando tablas: {e}", err=True)


@data_ops_group.command("seed")
@click.option(
    "--jobs", default=20, help="Número de ofertas de trabajo a generar y sembrar.", type=int
)
@click.option(
    "--candidates", default=50, help="Número de candidatos a generar y sembrar.", type=int
)
@with_appcontext
def db_seed(jobs, candidates):
    """Siembra la base de datos con datos simulados de trabajos y candidatos."""
    # Explicitly load .env here to ensure GEMINI_API_KEY is available for simulation
    dotenv_path = os.path.join(current_app.root_path, '..', '.env') # Assuming .env is in project root, one level up from adflux dir
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True) # Override to ensure it re-reads if already loaded
    else:
        click.echo(f"Warning: .env file not found at {dotenv_path} for db_seed command.", err=True)

    click.echo(f"Sembrando base de datos con {jobs} trabajos y {candidates} candidatos...")

    # Asegurar que las operaciones estén dentro del contexto de la app Flask para gestión de sesión
    with current_app.app_context():
        try:
            # Eliminar todas las tablas y recrearlas basadas en modelos actuales
            click.echo("Eliminando tablas existentes...")
            db.drop_all()
            click.echo("Creando tablas basadas en modelos actuales...")
            db.create_all()

            click.echo(f"Generando {jobs} trabajos y {candidates} candidatos...")
            # Generar datos
            generated_jobs = generate_multiple_jobs(jobs)
            generated_candidates = generate_multiple_candidates(candidates)

            # Sembrar trabajos
            click.echo(f"Sembrando {len(generated_jobs)} trabajos en la base de datos...")
            for job_data in generated_jobs:
                # Convertir fechas de string a objetos date
                if "posting_date" in job_data and job_data["posting_date"]:
                    job_data["posting_date"] = datetime.datetime.fromisoformat(
                        job_data["posting_date"].replace("Z", "+00:00")
                    ).date()
                if "closing_date" in job_data and job_data["closing_date"]:
                    job_data["closing_date"] = datetime.datetime.fromisoformat(
                        job_data["closing_date"].replace("Z", "+00:00")
                    ).date()

                # Mapear 'requirements' a 'required_skills' para el modelo
                if "requirements" in job_data:
                    job_data["required_skills"] = job_data.pop("requirements")

                # Convertir salary_range "$3.000.000 - $4.500.000" a enteros salary_min/salary_max
                if "salary_range" in job_data and job_data["salary_range"]:
                    range_text = job_data.pop("salary_range")
                    try:
                        # Remover símbolos y separar por '-'
                        parts = range_text.split("-")
                        if len(parts) == 2:
                            salary_min_raw = re.sub(r"[^0-9]", "", parts[0])
                            salary_max_raw = re.sub(r"[^0-9]", "", parts[1])
                            if salary_min_raw:
                                job_data["salary_min"] = int(salary_min_raw)
                            if salary_max_raw:
                                job_data["salary_max"] = int(salary_max_raw)
                    except Exception:
                        pass  # Si falla, ignorar y continuar

                # Asegurar que job_id es cadena
                if "job_id" in job_data:
                    job_data["job_id"] = str(job_data["job_id"])

                # Crear objeto JobOpening
                job = JobOpening(**job_data)
                db.session.add(job)

            # Confirmar para obtener IDs de trabajo antes de sembrar candidatos
            db.session.commit()
            click.echo(f"Sembrados {len(generated_jobs)} trabajos exitosamente.")

            # Sembrar candidatos
            click.echo(f"Sembrando {len(generated_candidates)} candidatos en la base de datos...")
            for candidate_data in generated_candidates:
                # Crear objeto Candidate
                candidate = Candidate(**candidate_data)
                db.session.add(candidate)

            # Confirmar cambios
            db.session.commit()
            click.echo(f"Sembrados {len(generated_candidates)} candidatos exitosamente.")

            # Generar algunas aplicaciones aleatorias
            click.echo("Generando aplicaciones aleatorias...")
            from ..simulation.application_data import generate_simulated_applications

            # Obtener trabajos y candidatos de la base de datos
            jobs_db = JobOpening.query.all()
            candidates_db = Candidate.query.all()

            # Convertir a formato esperado por la función de simulación
            jobs_list = [
                {
                    "job_id": job.job_id,
                    "status": job.status,
                    "posting_date": job.posted_date.isoformat() if job.posted_date else None,
                    "closing_date": job.closing_date.isoformat() if job.closing_date else None,
                }
                for job in jobs_db
            ]
            candidates_list = [
                {"candidate_id": candidate.candidate_id} for candidate in candidates_db
            ]

            # Generar aplicaciones simuladas
            applications = generate_simulated_applications(
                jobs_list, candidates_list, min(len(jobs_db) * 2, len(candidates_db))
            )

            # Sembrar aplicaciones
            click.echo(f"Sembrando {len(applications)} aplicaciones en la base de datos...")
            from ..models import Application

            for app_data in applications:
                # Convertir fecha de string a objeto date
                if "application_date" in app_data and app_data["application_date"]:
                    app_data["application_date"] = datetime.datetime.fromisoformat(
                        app_data["application_date"].replace("Z", "+00:00")
                    ).date()

                # Crear objeto Application
                application = Application(**app_data)
                db.session.add(application)

            # Confirmar cambios
            db.session.commit()
            click.echo(f"Sembradas {len(applications)} aplicaciones exitosamente.")

            click.echo("Siembra de datos completada exitosamente.")

        except Exception as e:
            db.session.rollback()
            click.echo(f"Error durante la siembra de datos: {e}", err=True)
            import traceback

            click.echo(traceback.format_exc())


@data_ops_group.command("reset")
@click.confirmation_option(prompt="¿Estás seguro de que quieres eliminar TODOS los datos?")
@with_appcontext
def db_reset():
    """Elimina todas las tablas y las recrea vacías."""
    with current_app.app_context():
        try:
            click.echo("Eliminando todas las tablas...")
            db.drop_all()
            click.echo("Creando tablas vacías...")
            db.create_all()
            click.echo("Base de datos reiniciada exitosamente.")
        except Exception as e:
            click.echo(f"Error reiniciando la base de datos: {e}", err=True)


@data_ops_group.command("export")
@click.argument(
    "model_name", type=click.Choice(["jobs", "candidates", "applications", "campaigns"])
)
@click.option("--output", "-o", default="export.json", help="Nombre del archivo de salida")
@with_appcontext
def db_export(model_name, output):
    """Exporta datos de un modelo específico a un archivo JSON."""
    with current_app.app_context():
        try:
            # Mapear nombres de modelos a clases
            model_map = {
                "jobs": JobOpening,
                "candidates": Candidate,
                "applications": db.session.registry._class_registry.get("Application"),
                "campaigns": db.session.registry._class_registry.get("Campaign"),
            }

            model_class = model_map.get(model_name)
            if not model_class:
                click.echo(f"Modelo no encontrado: {model_name}", err=True)
                return

            # Consultar todos los registros
            records = model_class.query.all()
            click.echo(f"Exportando {len(records)} registros de {model_name}...")

            # Convertir a diccionarios
            data = []
            for record in records:
                # Convertir objeto a diccionario
                record_dict = {}
                for column in model_class.__table__.columns:
                    value = getattr(record, column.name)
                    # Convertir tipos no serializables
                    if isinstance(value, datetime.date):
                        value = value.isoformat()
                    record_dict[column.name] = value
                data.append(record_dict)

            # Guardar a archivo
            with open(output, "w") as f:
                json.dump(data, f, indent=2)

            click.echo(f"Datos exportados exitosamente a {output}")

        except Exception as e:
            click.echo(f"Error exportando datos: {e}", err=True)
            import traceback

            click.echo(traceback.format_exc())
