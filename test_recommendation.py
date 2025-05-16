"""
Script para probar el sistema de recomendación.
"""

from adflux.models import JobOpening
from adflux.core.factory import create_app
from adflux.services.recommendation_service import RecommendationService

app = create_app()

with app.app_context():
    print("Trabajos disponibles:")
    jobs = JobOpening.query.all()
    for job in jobs:
        print(f"- {job.job_id}: {job.title}")
    
    if jobs:
        print("\nProbando sistema de recomendación...")
        recommendation_service = RecommendationService()
        job_id = jobs[0].job_id
        
        success, message, recommendations = recommendation_service.get_job_recommendations(job_id)
        
        print(f"Resultado: {'Éxito' if success else 'Error'}")
        print(f"Mensaje: {message}")
        
        if success: 
            print("\nRecomendaciones generadas:")
            print(f"Mejor plataforma: {recommendations['best_platform']}")
            print(f"Confianza: {recommendations['confidence_score']}%")
            print(f"Basado en datos históricos: {'Sí' if recommendations['based_on_historical'] else 'No'}")
            
            print("\nRanking de plataformas:")
            for platform in recommendations['platform_ranking']:
                print(f"- {platform['platform']}: {platform['score']:.2f} puntos (CTR: {platform['ctr']:.2f}%, Conv: {platform.get('conversion_rate', 0):.2f}%)")
            
            print("\nPresupuesto recomendado:")
            budget = recommendations['recommended_budget']
            print(f"- Mínimo: ${budget['daily_min']/100:.2f}/día")
            print(f"- Recomendado: ${budget['daily_recommended']/100:.2f}/día")
            print(f"- Máximo: ${budget['daily_max']/100:.2f}/día")
    else:
        print("No hay trabajos disponibles para probar el sistema de recomendación.")
