"""
Rutas web para trabajos en AdFlux.

Este módulo contiene las rutas web relacionadas con la gestión de trabajos.
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Optional
import json
from datetime import datetime
import uuid

from ..models import JobOpening, db

job_bp = Blueprint("job", __name__, template_folder="../templates")


class JobForm(FlaskForm):
    """Formulario para crear y editar trabajos."""
    title = StringField('Título', validators=[DataRequired()])
    short_description = StringField('Descripción Corta', validators=[Optional()])
    description = TextAreaField('Descripción Completa', validators=[Optional()])
    company_name = StringField('Empresa', validators=[Optional()])
    location = StringField('Ubicación', validators=[Optional()])
    department = StringField('Departamento', validators=[Optional()])
    salary_min = IntegerField('Salario Mínimo', validators=[Optional()])
    salary_max = IntegerField('Salario Máximo', validators=[Optional()])
    employment_type = SelectField('Tipo de Empleo', choices=[
        ('', 'Seleccionar...'),
        ('full-time', 'Tiempo Completo'),
        ('part-time', 'Medio Tiempo'),
        ('contract', 'Contrato'),
        ('temporary', 'Temporal'),
        ('internship', 'Pasantía')
    ], validators=[Optional()])
    experience_level = SelectField('Nivel de Experiencia', choices=[
        ('', 'Seleccionar...'),
        ('entry-level', 'Nivel de Entrada'),
        ('mid-level', 'Nivel Medio'),
        ('senior', 'Senior'),
        ('executive', 'Ejecutivo')
    ], validators=[Optional()])
    education_level = SelectField('Nivel de Educación', choices=[
        ('', 'Seleccionar...'),
        ('high-school', 'Bachillerato'),
        ('associate', 'Técnico/Tecnólogo'),
        ('bachelor', 'Pregrado'),
        ('master', 'Maestría'),
        ('doctorate', 'Doctorado')
    ], validators=[Optional()])
    posted_date = DateField('Fecha de Publicación', format='%Y-%m-%d', validators=[Optional()])
    closing_date = DateField('Fecha de Cierre', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Estado', choices=[
        ('open', 'Abierto'),
        ('closed', 'Cerrado'),
        ('draft', 'Borrador')
    ], default='open')
    remote = BooleanField('Trabajo Remoto', default=False)
    required_skills = TextAreaField('Habilidades Requeridas', validators=[Optional()])
    benefits = TextAreaField('Beneficios', validators=[Optional()])


@job_bp.route("/")
def list_jobs():
    """Renderiza la página de lista de empleos."""
    try:
        jobs = JobOpening.query.order_by(JobOpening.posted_date.desc()).all()
    except Exception as e:
        flash(f"Error al obtener empleos: {e}", "error")
        jobs = []  # Asegurar que jobs sea siempre una lista
    return render_template("jobs_list.html", title="Ofertas de Empleo", jobs=jobs)


@job_bp.route("/<string:job_id>")
def job_details(job_id):
    """Renderiza la página de detalles para una oferta de empleo específica."""
    job = JobOpening.query.filter_by(job_id=job_id).first_or_404()
    return render_template("job_detail.html", title=f"Empleo: {job.title}", job=job)


@job_bp.route("/create", methods=["GET", "POST"])
def create_job():
    """Renderiza y procesa el formulario para crear un nuevo trabajo."""
    form = JobForm()
    
    if form.validate_on_submit():
        try:
            job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
            
            required_skills = [skill.strip() for skill in form.required_skills.data.split(',')] if form.required_skills.data else []
            benefits = [benefit.strip() for benefit in form.benefits.data.split(',')] if form.benefits.data else []
            
            new_job = JobOpening(
                job_id=job_id,
                title=form.title.data,
                short_description=form.short_description.data,
                description=form.description.data,
                company_name=form.company_name.data,
                location=form.location.data,
                department=form.department.data,
                salary_min=form.salary_min.data,
                salary_max=form.salary_max.data,
                employment_type=form.employment_type.data,
                experience_level=form.experience_level.data,
                education_level=form.education_level.data,
                posted_date=form.posted_date.data or datetime.now().date(),
                closing_date=form.closing_date.data,
                status=form.status.data,
                remote=form.remote.data,
                required_skills=required_skills,
                benefits=benefits
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            flash(f"Trabajo '{new_job.title}' creado exitosamente.", "success")
            return redirect(url_for('job.job_details', job_id=new_job.job_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear trabajo: {e}", "error")
    
    return render_template("job_form.html", title="Crear Trabajo", form=form, job=None)


@job_bp.route("/<string:job_id>/edit", methods=["GET", "POST"])
def update_job(job_id):
    """Renderiza y procesa el formulario para editar un trabajo existente."""
    job = JobOpening.query.filter_by(job_id=job_id).first_or_404()
    form = JobForm(obj=job)
    
    if request.method == "GET":
        form.required_skills.data = ', '.join(job.required_skills) if job.required_skills else ''
        form.benefits.data = ', '.join(job.benefits) if job.benefits else ''
    
    if form.validate_on_submit():
        try:
            job.title = form.title.data
            job.short_description = form.short_description.data
            job.description = form.description.data
            job.company_name = form.company_name.data
            job.location = form.location.data
            job.department = form.department.data
            job.salary_min = form.salary_min.data
            job.salary_max = form.salary_max.data
            job.employment_type = form.employment_type.data
            job.experience_level = form.experience_level.data
            job.education_level = form.education_level.data
            job.posted_date = form.posted_date.data
            job.closing_date = form.closing_date.data
            job.status = form.status.data
            job.remote = form.remote.data
            
            job.required_skills = [skill.strip() for skill in form.required_skills.data.split(',')] if form.required_skills.data else []
            job.benefits = [benefit.strip() for benefit in form.benefits.data.split(',')] if form.benefits.data else []
            
            db.session.commit()
            
            flash(f"Trabajo '{job.title}' actualizado exitosamente.", "success")
            return redirect(url_for('job.job_details', job_id=job.job_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar trabajo: {e}", "error")
    
    return render_template("job_form.html", title="Editar Trabajo", form=form, job=job)
