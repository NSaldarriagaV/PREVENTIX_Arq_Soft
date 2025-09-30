# Inversión de Dependencias - Sistema de Recomendaciones

## 📋 Resumen

Este documento describe la implementación del **Principio de Inversión de Dependencias (DIP)** en el sistema de recomendaciones de citas médicas del proyecto PREVENTIX.

## 🎯 Objetivo

Refactorizar el sistema de recomendaciones para:
- **Reducir el acoplamiento** entre las vistas y las implementaciones específicas de ML
- **Facilitar el testing** con servicios mock
- **Permitir el intercambio** de algoritmos de recomendación sin modificar el código cliente
- **Mejorar la mantenibilidad** y extensibilidad del sistema

## 🏗️ Arquitectura Antes vs Después

### ❌ **ANTES (Alto Acoplamiento)**
```python
# appointments/views.py
from .ml_model import recommend_appointments  # Dependencia directa

def appointment_recommendations(request):
    recommendations = recommend_appointments(user_id)  # Acoplamiento fuerte
```

### ✅ **DESPUÉS (Bajo Acoplamiento)**
```python
# appointments/views.py
from .recommendation_factory import get_recommendation_service  # Dependencia de abstracción

def appointment_recommendations(request):
    service = get_recommendation_service()  # Inyección de dependencia
    recommendations = service.get_recommendations(user_id)  # Uso de interfaz
```

## 📁 Estructura de Archivos

```
appointments/
├── recommendation_interface.py          # 🎯 Interfaz abstracta
├── knn_recommendation_service.py       # 🔧 Implementación KNN
├── mock_recommendation_service.py      # 🧪 Implementación Mock
├── recommendation_factory.py            # 🏭 Factory + DI Container
├── test_recommendation_service.py      # ✅ Tests
└── DEPENDENCY_INVERSION_DOCUMENTATION.md # 📚 Documentación
```

## 🔧 Componentes Implementados

### 1. **Interfaz Abstracta** (`recommendation_interface.py`)
```python
class RecommendationService(ABC):
    @abstractmethod
    def train_model(self) -> bool: ...
    
    @abstractmethod
    def get_recommendations(self, user_id: int) -> pd.DataFrame: ...
    
    @abstractmethod
    def is_model_available(self) -> bool: ...
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]: ...
```

### 2. **Implementación KNN** (`knn_recommendation_service.py`)
- Refactoriza el código original de `ml_model.py`
- Encapsula lógica de entrenamiento y predicción
- Mantiene compatibilidad con funcionalidad existente

### 3. **Implementación Mock** (`mock_recommendation_service.py`)
- Para testing y desarrollo
- Retorna datos simulados
- No requiere entrenamiento de modelos reales

### 4. **Factory + DI Container** (`recommendation_factory.py`)
```python
class RecommendationServiceFactory:
    @classmethod
    def create_service(cls, service_type: str) -> RecommendationService: ...
    
    @classmethod
    def create_from_settings(cls) -> RecommendationService: ...

def get_recommendation_service() -> RecommendationService:  # Singleton
```

## ⚙️ Configuración

### Settings.py
```python
# Configuración del servicio de recomendaciones
RECOMMENDATION_SERVICE_TYPE = 'knn'  # 'knn' o 'mock'
KNN_MODEL_PATH = 'appointments/models/knn_model.pkl'
KNN_N_NEIGHBORS = 3
```

### Uso en Vistas
```python
from .recommendation_factory import get_recommendation_service

def appointment_recommendations(request):
    service = get_recommendation_service()
    recommendations = service.get_recommendations(user_id)
```

## 🧪 Testing

### Ejecutar Tests
```bash
python manage.py test appointments.test_recommendation_service
```

### Tests Implementados
- ✅ Verificación de contrato de interfaz
- ✅ Tests del factory
- ✅ Tests del patrón Singleton
- ✅ Tests de inyección de dependencias
- ✅ Tests específicos de MockRecommendationService

## 🚀 Beneficios Obtenidos

### 1. **Flexibilidad**
- Cambiar algoritmo: Solo modificar `RECOMMENDATION_SERVICE_TYPE`
- Agregar nuevos algoritmos: Implementar `RecommendationService`

### 2. **Testabilidad**
- Testing sin dependencias de ML reales
- Mock services para desarrollo rápido

### 3. **Mantenibilidad**
- Código más limpio y organizado
- Separación clara de responsabilidades
- Fácil extensión del sistema

### 4. **Configurabilidad**
- Configuración centralizada en settings
- Diferentes servicios para diferentes entornos

## 📈 Ejemplos de Uso

### Cambiar a Mock para Testing
```python
# En settings.py
RECOMMENDATION_SERVICE_TYPE = 'mock'
```

### Usar KNN en Producción
```python
# En settings.py
RECOMMENDATION_SERVICE_TYPE = 'knn'
```

### Agregar Nuevo Algoritmo
```python
# 1. Crear nueva implementación
class CollaborativeFilteringService(RecommendationService):
    def train_model(self) -> bool: ...
    def get_recommendations(self, user_id: int) -> pd.DataFrame: ...
    # ... otros métodos

# 2. Registrar en factory
RecommendationServiceFactory.register_service('collaborative', CollaborativeFilteringService)

# 3. Configurar en settings
RECOMMENDATION_SERVICE_TYPE = 'collaborative'
```

## 🔄 Comandos de Management

### Entrenar Modelo
```bash
# Usar servicio configurado
python manage.py train_model

# Usar servicio específico
python manage.py train_model --service mock
python manage.py train_model --service knn
```

## 📊 Métricas de Mejora

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Acoplamiento** | Alto (dependencia directa) | Bajo (dependencia de abstracción) |
| **Testabilidad** | Difícil (requiere datos reales) | Fácil (mock services) |
| **Extensibilidad** | Difícil (modificar código) | Fácil (nueva implementación) |
| **Configurabilidad** | Ninguna | Alta (settings + factory) |

## 🎯 Principios SOLID Aplicados

- ✅ **S** - Single Responsibility: Cada clase tiene una responsabilidad
- ✅ **O** - Open/Closed: Abierto para extensión, cerrado para modificación
- ✅ **L** - Liskov Substitution: Implementaciones son intercambiables
- ✅ **I** - Interface Segregation: Interfaz específica y cohesiva
- ✅ **D** - Dependency Inversion: Dependencias de abstracciones, no concreciones

## 🚀 Próximos Pasos

1. **Implementar más algoritmos**: Collaborative Filtering, Content-Based
2. **A/B Testing**: Comparar rendimiento de diferentes algoritmos
3. **Métricas**: Agregar logging y monitoreo de recomendaciones
4. **Caching**: Implementar cache para recomendaciones frecuentes
5. **API**: Exponer servicios de recomendación via REST API

---

**Fecha de implementación**: Febrero 2025  
**Autor**: Juan Esteban Romero  
**Rama**: juanes
