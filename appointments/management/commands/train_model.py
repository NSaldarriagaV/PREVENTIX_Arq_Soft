from django.core.management.base import BaseCommand
from appointments.recommendation_factory import get_recommendation_service


class Command(BaseCommand):
    help = 'Entrena el modelo de recomendaciones usando el servicio configurado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--service',
            type=str,
            default=None,
            help='Tipo de servicio a usar (knn, mock). Si no se especifica, usa la configuración por defecto.'
        )

    def handle(self, *args, **options):
        service_type = options['service']
        
        if service_type:
            from appointments.recommendation_factory import RecommendationServiceFactory
            recommendation_service = RecommendationServiceFactory.create_service(service_type)
            self.stdout.write(f'Usando servicio: {service_type}')
        else:
            recommendation_service = get_recommendation_service()
            self.stdout.write('Usando servicio configurado en settings')
        
        self.stdout.write('Iniciando entrenamiento del modelo...')
        
        if recommendation_service.train_model():
            self.stdout.write(
                self.style.SUCCESS('Modelo entrenado exitosamente!')
            )
            
            # Mostrar información del modelo
            model_info = recommendation_service.get_model_info()
            self.stdout.write(f'Información del modelo: {model_info}')
        else:
            self.stdout.write(
                self.style.ERROR('Error entrenando el modelo')
            )
