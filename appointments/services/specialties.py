from django.db.models import Count
from appointments.models import Appointment
from .factory import build_specialty_strategy

ALL_SPECIALTIES = [
    'Odontología', 'Vacunación', 'Chequeo general', 'Dermatología', 'Oftalmología',
    'Cardiología', 'Ginecología', 'Urología', 'Pediatría', 'Otorrinolaringología',
    'Medicina interna', 'Endocrinología', 'Nutrición', 'Psicología', 'Psiquiatría',
    'Neumología', 'Fisioterapia', 'Rehabilitación', 'Neurología', 'Revisión postoperatoria',
    'Análisis de laboratorio', 'Control de peso', 'Revisión de medicamentos',
    'Consulta virtual', 'Medicina del deporte'
]


def get_specialty_choices_for_user(user):
    """
    Retorna: (specialty_choices, frequent, others)
    - specialty_choices: lista de tuplas (valor, etiqueta) para el <select>
    - frequent: especialidades del usuario (por uso)
    - others: resto de especialidades
    """
    counters = (
        Appointment.objects.for_user(user)
        .filter(specialty__in=ALL_SPECIALTIES)
        .values('specialty')
        .annotate(count=Count('specialty'))
    )
    user_counts = {row['specialty']: row['count'] for row in counters}

    strategy = build_specialty_strategy()
    ordered = strategy.order(ALL_SPECIALTIES, user_counts)

    frequent = [s for s in ordered if s in user_counts]
    others = [s for s in ordered if s not in user_counts]
    specialty_choices = [(s, s) for s in ordered]
    return specialty_choices, frequent, others
