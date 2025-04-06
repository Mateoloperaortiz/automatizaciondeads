"""
Modelo de campaña para AdFlux.

Este módulo contiene el modelo Campaign que representa una campaña publicitaria
en AdFlux, que puede ser publicada en diferentes plataformas.
"""

import datetime
from sqlalchemy import String, Text, Integer, DateTime, JSON
from . import db


class Campaign(db.Model):
    """
    Modelo que representa un concepto de campaña AdFlux de alto nivel.

    Una campaña AdFlux es una abstracción de alto nivel que puede ser publicada
    en diferentes plataformas como Meta, Google, etc. Contiene información sobre
    el presupuesto, el trabajo asociado, los segmentos objetivo, etc.
    """

    __tablename__ = "campaigns"

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    platform = db.Column(
        String(50), nullable=False, index=True
    )  # ej., 'meta', 'linkedin', 'google'
    status = db.Column(
        String(50), nullable=False, default="draft", index=True
    )  # ej., 'borrador', 'activa', 'pausada', 'archivada'

    # Presupuesto (en centavos)
    daily_budget = db.Column(Integer, nullable=True)  # ej., 500 para $5.00

    # Fechas
    start_date = db.Column(DateTime, nullable=True)
    end_date = db.Column(DateTime, nullable=True)

    # Enlace a la oferta de trabajo específica para la que es esta campaña
    job_opening_id = db.Column(String(50), db.ForeignKey("job_openings.job_id"), nullable=True)

    # Almacenar lista de IDs de segmentos objetivo (de nuestro modelo ML)
    target_segment_ids = db.Column(JSON, nullable=True)

    # Campos del Creativo Publicitario
    primary_text = db.Column(String(200), nullable=True)
    headline = db.Column(String(40), nullable=True)
    link_description = db.Column(String(50), nullable=True)
    creative_image_filename = db.Column(
        String(255), nullable=True
    )  # Nombre de archivo de la imagen subida

    # URL de destino
    landing_page_url = db.Column(String(255), nullable=True)

    # Configuración específica de plataforma
    meta_ad_account_id = db.Column(String(50), nullable=True)
    meta_page_id = db.Column(String(50), nullable=True)
    meta_objective = db.Column(String(50), nullable=True)
    google_customer_id = db.Column(String(50), nullable=True)
    targeting_spec = db.Column(JSON, nullable=True)
    initial_status = db.Column(String(50), nullable=True, default="PAUSED")

    # Almacenar IDs después de publicar en la plataforma externa
    external_id = db.Column(String(255), nullable=True, index=True)
    external_ids = db.Column(JSON, nullable=True)

    # IDs específicos de plataforma
    meta_ad_set_id = db.Column(String(255), nullable=True)
    meta_ad_id = db.Column(String(255), nullable=True)
    google_ad_group_id = db.Column(String(255), nullable=True)
    google_ad_id = db.Column(String(255), nullable=True)

    # Campos de auditoría
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Propiedades para compatibilidad con código existente
    @property
    def ad_text(self):
        return self.primary_text

    @property
    def ad_headline(self):
        return self.headline

    @property
    def ad_description(self):
        return self.link_description

    def __repr__(self):
        return f"<Campaign {self.id}: {self.name} ({self.platform} - {self.status})>"
