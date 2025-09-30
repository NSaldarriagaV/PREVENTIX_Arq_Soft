"""
Implementación concreta del servicio de recomendaciones usando KNN.
Implementa RecommendationService siguiendo el principio de inversión de dependencias.
"""
import os
import joblib
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from django.db.models import Count, Max
from django.utils import timezone
from .models import Appointment
from .recommendation_interface import RecommendationService
from typing import Dict, Any


class KNNRecommendationService(RecommendationService):
    """
    Implementación concreta del servicio de recomendaciones usando K-Nearest Neighbors.
    Refactoriza el código original para seguir el principio de inversión de dependencias.
    """
    
    def __init__(self, model_path: str = 'appointments/models/knn_model.pkl', n_neighbors: int = 3):
        """
        Inicializa el servicio KNN.
        
        Args:
            model_path (str): Ruta donde se guarda el modelo entrenado
            n_neighbors (int): Número de vecinos más cercanos para KNN
        """
        self.model_path = model_path
        self.n_neighbors = n_neighbors
        self.model = None
        self.model_trained_at = None
    
    def train_model(self) -> bool:
        """
        Entrena el modelo KNN con los datos de citas disponibles.
        
        Returns:
            bool: True si el entrenamiento fue exitoso, False en caso contrario
        """
        try:
            # Obtener datos de citas
            appointments = (
                Appointment.objects
                .exclude(specialty__isnull=True)
                .exclude(specialty='')
                .values('user_id', 'specialty')
                .annotate(count=Count('id'), last_date=Max('date'))
            )
            
            # Convertir a DataFrame
            data = pd.DataFrame(appointments)
            if data.empty:
                print("No hay datos suficientes para entrenar el modelo.")
                return False
            
            # Procesar campos
            data['last_date'] = pd.to_datetime(data['last_date'])
            data['date'] = data['last_date'].map(lambda x: x.timestamp())
            X = data[['user_id', 'count', 'date']]
            
            # Entrenar modelo KNN
            self.model = NearestNeighbors(n_neighbors=self.n_neighbors)
            self.model.fit(X)
            
            # Guardar modelo
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            
            # Guardar timestamp de entrenamiento
            self.model_trained_at = timezone.now()
            
            print("Modelo KNN entrenado y guardado correctamente.")
            return True
            
        except Exception as e:
            print(f"Error entrenando el modelo: {e}")
            return False
    
    def get_recommendations(self, user_id: int) -> pd.DataFrame:
        """
        Obtiene recomendaciones de citas para un usuario específico usando KNN.
        
        Args:
            user_id (int): ID del usuario para el cual generar recomendaciones
            
        Returns:
            pd.DataFrame: DataFrame con las recomendaciones (specialty, formatted_date)
        """
        try:
            # Verificar si el modelo existe, si no, entrenarlo
            if not self.is_model_available():
                if not self.train_model():
                    return pd.DataFrame()
            
            # Cargar modelo si no está en memoria
            if self.model is None:
                self.model = joblib.load(self.model_path)
            
            # Obtener datos del usuario
            appointments = (
                Appointment.objects
                .filter(user_id=user_id)
                .exclude(specialty__isnull=True)
                .exclude(specialty='')
                .values('specialty')
                .annotate(count=Count('id'), last_date=Max('date'))
            )
            
            df = pd.DataFrame(appointments)
            if df.empty:
                return pd.DataFrame()
            
            # Preparar datos para predicción
            df['user_id'] = user_id
            df['last_date'] = pd.to_datetime(df['last_date'])
            df['timestamp'] = df['last_date'].apply(lambda x: x.timestamp())
            df['date'] = df['timestamp']
            df = df.dropna(subset=['count', 'date'])
            
            if df.empty:
                return pd.DataFrame()
            
            # Obtener recomendaciones
            n_neighbors = min(self.n_neighbors, len(df))
            distances, indices = self.model.kneighbors(
                df[['user_id', 'count', 'date']], 
                n_neighbors=n_neighbors
            )
            
            # Filtrar índices válidos
            valid_indices = [i for i in indices[0] if i < len(df)]
            if not valid_indices:
                return pd.DataFrame()
            
            # Preparar resultado
            recommended = df.iloc[valid_indices].copy()
            recommended.loc[:, 'formatted_date'] = recommended['last_date'].apply(
                lambda x: x.strftime('%Y-%m-%d')
            )
            
            return recommended[['specialty', 'formatted_date']]
            
        except Exception as e:
            print(f"Error obteniendo recomendaciones: {e}")
            return pd.DataFrame()
    
    def is_model_available(self) -> bool:
        """
        Verifica si el modelo está disponible y listo para usar.
        
        Returns:
            bool: True si el modelo está disponible, False en caso contrario
        """
        return os.path.exists(self.model_path)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo actual.
        
        Returns:
            Dict[str, Any]: Información del modelo
        """
        return {
            'type': 'KNN',
            'model_path': self.model_path,
            'n_neighbors': self.n_neighbors,
            'is_available': self.is_model_available(),
            'trained_at': self.model_trained_at.isoformat() if self.model_trained_at else None
        }
