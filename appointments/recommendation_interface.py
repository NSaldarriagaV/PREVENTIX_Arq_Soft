"""
Interfaz para el sistema de recomendaciones de citas médicas.
Implementa el principio de inversión de dependencias (DIP).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class RecommendationService(ABC):
    """
    Interfaz abstracta para servicios de recomendación de citas médicas.
    Permite diferentes implementaciones (KNN, Collaborative Filtering, etc.)
    """
    
    @abstractmethod
    def train_model(self) -> bool:
        """
        Entrena el modelo de recomendación con los datos disponibles.
        
        Returns:
            bool: True si el entrenamiento fue exitoso, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_recommendations(self, user_id: int) -> pd.DataFrame:
        """
        Obtiene recomendaciones de citas para un usuario específico.
        
        Args:
            user_id (int): ID del usuario para el cual generar recomendaciones
            
        Returns:
            pd.DataFrame: DataFrame con las recomendaciones (specialty, formatted_date)
        """
        pass
    
    @abstractmethod
    def is_model_available(self) -> bool:
        """
        Verifica si el modelo está disponible y listo para usar.
        
        Returns:
            bool: True si el modelo está disponible, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo actual.
        
        Returns:
            Dict[str, Any]: Información del modelo (tipo, fecha de entrenamiento, etc.)
        """
        pass
