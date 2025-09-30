"""
Tests para verificar que la inversión de dependencias funciona correctamente.
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from django.test import TestCase
from django.contrib.auth import get_user_model
from .recommendation_interface import RecommendationService
from .knn_recommendation_service import KNNRecommendationService
from .mock_recommendation_service import MockRecommendationService
from .recommendation_factory import RecommendationServiceFactory, get_recommendation_service, reset_recommendation_service

User = get_user_model()


class TestRecommendationServiceInterface(TestCase):
    """Tests para verificar que las implementaciones siguen el contrato de la interfaz."""
    
    def test_knn_service_implements_interface(self):
        """Verifica que KNNRecommendationService implementa RecommendationService."""
        service = KNNRecommendationService()
        self.assertIsInstance(service, RecommendationService)
    
    def test_mock_service_implements_interface(self):
        """Verifica que MockRecommendationService implementa RecommendationService."""
        service = MockRecommendationService()
        self.assertIsInstance(service, RecommendationService)
    
    def test_mock_service_methods(self):
        """Verifica que MockRecommendationService implementa todos los métodos requeridos."""
        service = MockRecommendationService()
        
        # Verificar que todos los métodos existen
        self.assertTrue(hasattr(service, 'train_model'))
        self.assertTrue(hasattr(service, 'get_recommendations'))
        self.assertTrue(hasattr(service, 'is_model_available'))
        self.assertTrue(hasattr(service, 'get_model_info'))
        
        # Verificar tipos de retorno
        self.assertIsInstance(service.train_model(), bool)
        self.assertIsInstance(service.is_model_available(), bool)
        self.assertIsInstance(service.get_model_info(), dict)
        
        # Verificar que get_recommendations retorna DataFrame
        recommendations = service.get_recommendations(1)
        self.assertIsInstance(recommendations, pd.DataFrame)


class TestRecommendationServiceFactory(TestCase):
    """Tests para el factory de servicios de recomendación."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        reset_recommendation_service()
    
    def test_create_knn_service(self):
        """Verifica que se puede crear un servicio KNN."""
        service = RecommendationServiceFactory.create_service('knn')
        self.assertIsInstance(service, KNNRecommendationService)
    
    def test_create_mock_service(self):
        """Verifica que se puede crear un servicio Mock."""
        service = RecommendationServiceFactory.create_service('mock')
        self.assertIsInstance(service, MockRecommendationService)
    
    def test_create_invalid_service(self):
        """Verifica que se lanza error para servicios inválidos."""
        with self.assertRaises(ValueError):
            RecommendationServiceFactory.create_service('invalid_service')
    
    def test_get_available_services(self):
        """Verifica que se pueden obtener los servicios disponibles."""
        services = RecommendationServiceFactory.get_available_services()
        self.assertIn('knn', services)
        self.assertIn('mock', services)
    
    def test_singleton_pattern(self):
        """Verifica que get_recommendation_service implementa el patrón Singleton."""
        service1 = get_recommendation_service()
        service2 = get_recommendation_service()
        self.assertIs(service1, service2)
    
    def test_reset_singleton(self):
        """Verifica que reset_recommendation_service funciona correctamente."""
        service1 = get_recommendation_service()
        reset_recommendation_service()
        service2 = get_recommendation_service()
        self.assertIsNot(service1, service2)


class TestMockRecommendationService(TestCase):
    """Tests específicos para MockRecommendationService."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.service = MockRecommendationService()
    
    def test_train_model_returns_true(self):
        """Verifica que train_model siempre retorna True."""
        result = self.service.train_model()
        self.assertTrue(result)
    
    def test_is_model_available_returns_true(self):
        """Verifica que is_model_available siempre retorna True."""
        result = self.service.is_model_available()
        self.assertTrue(result)
    
    def test_get_recommendations_returns_dataframe(self):
        """Verifica que get_recommendations retorna un DataFrame válido."""
        recommendations = self.service.get_recommendations(1)
        
        self.assertIsInstance(recommendations, pd.DataFrame)
        self.assertIn('specialty', recommendations.columns)
        self.assertIn('formatted_date', recommendations.columns)
    
    def test_get_model_info_returns_dict(self):
        """Verifica que get_model_info retorna un diccionario con información válida."""
        info = self.service.get_model_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['type'], 'Mock')
        self.assertTrue(info['is_available'])


class TestDependencyInjection(TestCase):
    """Tests para verificar que la inyección de dependencias funciona correctamente."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        reset_recommendation_service()
    
    @patch('appointments.recommendation_factory.RecommendationServiceFactory.create_from_settings')
    def test_get_recommendation_service_uses_factory(self, mock_create):
        """Verifica que get_recommendation_service usa el factory."""
        mock_service = MagicMock()
        mock_create.return_value = mock_service
        
        service = get_recommendation_service()
        
        self.assertEqual(service, mock_service)
        mock_create.assert_called_once()
    
    def test_service_switching(self):
        """Verifica que se puede cambiar entre diferentes servicios."""
        # Crear servicio mock
        mock_service = RecommendationServiceFactory.create_service('mock')
        reset_recommendation_service()
        
        # Verificar que se puede obtener el servicio configurado
        service = get_recommendation_service()
        self.assertIsNotNone(service)


if __name__ == '__main__':
    unittest.main()
