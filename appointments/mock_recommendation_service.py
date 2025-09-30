"""
Implementación mock del servicio de recomendaciones para testing.
Implementa RecommendationService siguiendo el principio de inversión de dependencias.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from .recommendation_interface import RecommendationService


class MockRecommendationService(RecommendationService):
    """
    Implementación mock del servicio de recomendaciones para testing y desarrollo.
    Retorna datos simulados sin necesidad de entrenar modelos reales.
    """
    
    def __init__(self):
        """Inicializa el servicio mock."""
        self.model_trained_at = None
        self.mock_data = {
            'specialties': [
                'Odontología', 'Vacunación', 'Chequeo general', 'Dermatología', 
                'Oftalmología', 'Cardiología', 'Ginecología', 'Urología'
            ]
        }
    
    def train_model(self) -> bool:
        """
        Simula el entrenamiento del modelo.
        
        Returns:
            bool: Siempre retorna True para simular éxito
        """
        self.model_trained_at = datetime.now()
        print("Modelo mock entrenado (simulado).")
        return True
    
    def get_recommendations(self, user_id: int) -> pd.DataFrame:
        """
        Obtiene recomendaciones simuladas para un usuario específico.
        
        Args:
            user_id (int): ID del usuario para el cual generar recomendaciones
            
        Returns:
            pd.DataFrame: DataFrame con recomendaciones simuladas
        """
        # Simular recomendaciones basadas en el user_id
        recommendations = []
        
        # Generar 2-4 recomendaciones simuladas
        import random
        num_recommendations = random.randint(2, 4)
        selected_specialties = random.sample(self.mock_data['specialties'], num_recommendations)
        
        for specialty in selected_specialties:
            # Generar fecha futura aleatoria (1-30 días)
            future_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
            recommendations.append({
                'specialty': specialty,
                'formatted_date': future_date.strftime('%Y-%m-%d')
            })
        
        return pd.DataFrame(recommendations)
    
    def is_model_available(self) -> bool:
        """
        Verifica si el modelo mock está disponible.
        
        Returns:
            bool: Siempre retorna True para el mock
        """
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo mock.
        
        Returns:
            Dict[str, Any]: Información del modelo mock
        """
        return {
            'type': 'Mock',
            'model_path': 'N/A (Mock Service)',
            'n_neighbors': 'N/A',
            'is_available': True,
            'trained_at': self.model_trained_at.isoformat() if self.model_trained_at else None,
            'description': 'Servicio mock para testing y desarrollo'
        }
