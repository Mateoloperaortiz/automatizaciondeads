"""
Script para probar la generación de creatividades.
"""

from adflux.models import JobOpening
from adflux.core.factory import create_app
from adflux.services.creative_service import CreativeService

app = create_app()

with app.app_context():
    print("Trabajos disponibles:")
    jobs = JobOpening.query.all()
    for job in jobs:
        print(f"- {job.job_id}: {job.title}")
    
    if jobs:
        print("\nProbando generación de creatividad...")
        creative_service = CreativeService()
        job_id = jobs[0].job_id
        platform = "meta"
        format_type = "imagen_única"
        
        success, message, content = creative_service.generate_ad_creative(
            job_id=job_id,
            platform=platform,
            format_type=format_type
        )
        
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
        
        if success:
            print("\nContenido generado:")
            for key, value in content.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"{key}: {value[:100]}...")
                else:
                    print(f"{key}: {value}")
    else:
        print("No hay trabajos disponibles para probar la generación de creatividades.")
