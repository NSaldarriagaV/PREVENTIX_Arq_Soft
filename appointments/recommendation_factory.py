"""
Factory para crear instancias de servicios de recomendación.
Implementa el patrón Factory para la inyección de dependencias.
"""
from django.conf import settings
from .recommendation_interface import RecommendationService
from .knn_recommendation_service import KNNRecommendationService
from .mock_recommendation_service import MockRecommendationService


class RecommendationServiceFactory:
    """
    Factory para crear instancias de servicios de recomendación.
    Centraliza la lógica de creación y configuración de servicios.
    """
    
    # Configuración por defecto
    DEFAULT_SERVICE = 'knn'
    AVAILABLE_SERVICES = {
        'knn': KNNRecommendationService,
        'mock': MockRecommendationService,
    }
    
    @classmethod
    def create_service(cls, service_type: str = None, **kwargs) -> RecommendationService:
        """
        Crea una instancia del servicio de recomendación especificado.
        
        Args:
            service_type (str, optional): Tipo de servicio a crear. 
                                        Si no se especifica, usa el valor por defecto.
            **kwargs: Argumentos adicionales para la inicialización del servicio.
            
        Returns:
            RecommendationService: Instancia del servicio de recomendación
            
        Raises:
            ValueError: Si el tipo de servicio no está disponible
        """
        if service_type is None:
            service_type = cls.DEFAULT_SERVICE
        
        if service_type not in cls.AVAILABLE_SERVICES:
            available_types = ', '.join(cls.AVAILABLE_SERVICES.keys())
            raise ValueError(f"Tipo de servicio '{service_type}' no disponible. "
                           f"Tipos disponibles: {available_types}")
        
        service_class = cls.AVAILABLE_SERVICES[service_type]
        return service_class(**kwargs)
    
    @classmethod
    def create_from_settings(cls) -> RecommendationService:
        """
        Crea un servicio de recomendación basado en la configuración de Django.
        
        Returns:
            RecommendationService: Instancia del servicio configurado
        """
        # Obtener configuración desde settings
        service_type = getattr(settings, 'RECOMMENDATION_SERVICE_TYPE', cls.DEFAULT_SERVICE)
        
        # Configuración específica para KNN
        knn_config = {}
        if service_type == 'knn':
            knn_config = {
                'model_path': getattr(settings, 'KNN_MODEL_PATH', 'appointments/models/knn_model.pkl'),
                'n_neighbors': getattr(settings, 'KNN_N_NEIGHBORS', 3)
            }
        
        return cls.create_service(service_type, **knn_config)
    
    @classmethod
    def get_available_services(cls) -> list:
        """
        Obtiene la lista de servicios disponibles.
        
        Returns:
            list: Lista de tipos de servicios disponibles
        """
        return list(cls.AVAILABLE_SERVICES.keys())
    
    @classmethod
    def register_service(cls, name: str, service_class: type):
        """
        Registra un nuevo tipo de servicio.
        
        Args:
            name (str): Nombre del servicio
            service_class (type): Clase que implementa RecommendationService
        """
        if not issubclass(service_class, RecommendationService):
            raise ValueError(f"La clase {service_class.__name__} debe implementar RecommendationService")
        
        cls.AVAILABLE_SERVICES[name] = service_class


# Instancia global del servicio (Singleton pattern)
_recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    """
    Obtiene la instancia global del servicio de recomendación.
    Implementa el patrón Singleton para evitar múltiples instancias.
    
    Returns:
        RecommendationService: Instancia del servicio de recomendación
    """
    global _recommendation_service
    
    if _recommendation_service is None:
        _recommendation_service = RecommendationServiceFactory.create_from_settings()
    
    return _recommendation_service


def reset_recommendation_service():
    """
    Resetea la instancia global del servicio.
    Útil para testing o cambio de configuración.
    """
    global _recommendation_service
    _recommendation_service = None
