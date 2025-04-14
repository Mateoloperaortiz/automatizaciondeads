"""
Pruebas de integración para la API de Gemini en AdFlux.

Este módulo contiene pruebas para verificar la integración con la API de Gemini AI.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from adflux.gemini.client import GeminiApiClient
from adflux.gemini.generation import generate_text, generate_ad_content, generate_job_description
from adflux.gemini.simulation import simulate_candidate_profile, simulate_job_opening


@pytest.mark.integration
class TestGeminiApi:
    """Pruebas para la API de Gemini."""
    
    @patch('adflux.gemini.client.genai')
    def test_gemini_api_client(self, mock_genai):
        """Prueba el cliente de la API de Gemini."""
        # Configurar mock
        mock_genai.configure.return_value = None
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Crear cliente
        client = GeminiApiClient(api_key='test_api_key')
        
        # Verificar que se configuró la API
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        
        # Verificar que se creó el modelo
        assert client.model == mock_model
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-pro-exp-03-25')
    
    @patch('adflux.gemini.generation.GeminiApiClient')
    def test_generate_text(self, mock_client_class):
        """Prueba la generación de texto con Gemini."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_model = MagicMock()
        mock_client.model = mock_model
        
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_response.text = "Generated text response"
        
        # Generar texto
        result = generate_text(
            prompt="Generate a creative text about AI",
            max_tokens=100,
            temperature=0.7,
            api_key='test_api_key'
        )
        
        # Verificar resultado
        assert result == "Generated text response"
        
        # Verificar que se llamó a generate_content
        mock_model.generate_content.assert_called_once()
        
        # Verificar parámetros
        args, kwargs = mock_model.generate_content.call_args
        assert "Generate a creative text about AI" in args[0]
        assert kwargs['generation_config'].max_output_tokens == 100
        assert kwargs['generation_config'].temperature == 0.7
    
    @patch('adflux.gemini.generation.GeminiApiClient')
    def test_generate_ad_content(self, mock_client_class):
        """Prueba la generación de contenido para anuncios con Gemini."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_model = MagicMock()
        mock_client.model = mock_model
        
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_response.text = json.dumps({
            "headline": "Join Our Team Today!",
            "description": "We're looking for talented individuals to join our growing company.",
            "cta": "Apply Now"
        })
        
        # Generar contenido para anuncio
        result = generate_ad_content(
            job_title="Software Developer",
            company_name="Tech Company",
            job_description="Develop software applications using Python and JavaScript",
            platform="META",
            format="feed",
            api_key='test_api_key'
        )
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert result["headline"] == "Join Our Team Today!"
        assert result["description"] == "We're looking for talented individuals to join our growing company."
        assert result["cta"] == "Apply Now"
        
        # Verificar que se llamó a generate_content
        mock_model.generate_content.assert_called_once()
        
        # Verificar parámetros
        args, kwargs = mock_model.generate_content.call_args
        assert "Software Developer" in args[0]
        assert "Tech Company" in args[0]
        assert "Python and JavaScript" in args[0]
        assert "META" in args[0]
        assert "feed" in args[0]
    
    @patch('adflux.gemini.generation.GeminiApiClient')
    def test_generate_job_description(self, mock_client_class):
        """Prueba la generación de descripciones de trabajo con Gemini."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_model = MagicMock()
        mock_client.model = mock_model
        
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_response.text = json.dumps({
            "title": "Senior Software Developer",
            "description": "We are seeking a Senior Software Developer to join our team...",
            "requirements": ["5+ years of experience", "Python expertise", "JavaScript knowledge"],
            "benefits": ["Competitive salary", "Remote work", "Health insurance"]
        })
        
        # Generar descripción de trabajo
        result = generate_job_description(
            job_title="Senior Software Developer",
            company_name="Tech Company",
            industry="Technology",
            skills=["Python", "JavaScript", "React"],
            experience_level="Senior",
            api_key='test_api_key'
        )
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert result["title"] == "Senior Software Developer"
        assert "We are seeking" in result["description"]
        assert "5+ years of experience" in result["requirements"]
        assert "Competitive salary" in result["benefits"]
        
        # Verificar que se llamó a generate_content
        mock_model.generate_content.assert_called_once()
        
        # Verificar parámetros
        args, kwargs = mock_model.generate_content.call_args
        assert "Senior Software Developer" in args[0]
        assert "Tech Company" in args[0]
        assert "Technology" in args[0]
        assert "Python" in args[0]
        assert "JavaScript" in args[0]
        assert "React" in args[0]
        assert "Senior" in args[0]
    
    @patch('adflux.gemini.simulation.GeminiApiClient')
    def test_simulate_candidate_profile(self, mock_client_class):
        """Prueba la simulación de perfiles de candidatos con Gemini."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_model = MagicMock()
        mock_client.model = mock_model
        
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_response.text = json.dumps({
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "New York, NY",
            "education": [
                {"degree": "Bachelor of Science", "field": "Computer Science", "institution": "NYU", "year": 2018}
            ],
            "experience": [
                {"title": "Software Developer", "company": "Tech Co", "years": 3, "description": "Developed web applications"}
            ],
            "skills": ["Python", "JavaScript", "React", "SQL"]
        })
        
        # Simular perfil de candidato
        result = simulate_candidate_profile(
            job_title="Software Developer",
            experience_level="Mid-level",
            location="New York",
            api_key='test_api_key'
        )
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert result["name"] == "John Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["location"] == "New York, NY"
        assert len(result["education"]) == 1
        assert len(result["experience"]) == 1
        assert len(result["skills"]) == 4
        
        # Verificar que se llamó a generate_content
        mock_model.generate_content.assert_called_once()
        
        # Verificar parámetros
        args, kwargs = mock_model.generate_content.call_args
        assert "Software Developer" in args[0]
        assert "Mid-level" in args[0]
        assert "New York" in args[0]
    
    @patch('adflux.gemini.simulation.GeminiApiClient')
    def test_simulate_job_opening(self, mock_client_class):
        """Prueba la simulación de ofertas de trabajo con Gemini."""
        # Configurar mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_model = MagicMock()
        mock_client.model = mock_model
        
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_response.text = json.dumps({
            "title": "Senior Software Developer",
            "company": "Tech Innovations Inc.",
            "location": "San Francisco, CA",
            "salary_range": {"min": 120000, "max": 150000},
            "employment_type": "Full-time",
            "description": "We are looking for a Senior Software Developer to join our team...",
            "requirements": ["5+ years of experience", "Python expertise", "JavaScript knowledge"],
            "benefits": ["Competitive salary", "Remote work", "Health insurance"]
        })
        
        # Simular oferta de trabajo
        result = simulate_job_opening(
            industry="Technology",
            company_size="Medium",
            location="San Francisco",
            api_key='test_api_key'
        )
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert result["title"] == "Senior Software Developer"
        assert result["company"] == "Tech Innovations Inc."
        assert result["location"] == "San Francisco, CA"
        assert isinstance(result["salary_range"], dict)
        assert result["employment_type"] == "Full-time"
        assert "We are looking for" in result["description"]
        assert len(result["requirements"]) == 3
        assert len(result["benefits"]) == 3
        
        # Verificar que se llamó a generate_content
        mock_model.generate_content.assert_called_once()
        
        # Verificar parámetros
        args, kwargs = mock_model.generate_content.call_args
        assert "Technology" in args[0]
        assert "Medium" in args[0]
        assert "San Francisco" in args[0]
