from django.shortcuts import render, redirect, get_object_or_404
from .forms import AppointmentForm
from .models import Appointment
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import date
from .recommendation_factory import get_recommendation_service
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime

# Lista solo las citas del usuario autenticado

@login_required
def appointment_list(request):
    today = date.today()

    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        date__gte=today
    ).order_by('date', 'time')

    past_appointments = Appointment.objects.filter(
        user=request.user,
        date__lt=today
    ).order_by('-date', '-time')  # Más recientes primero en las pasadas

    return render(request, 'appointments/list.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

# Edita solo citas del usuario autenticado
@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, user=request.user)

    # Lista completa de especialidades posibles
    all_specialties = [
        'Odontología', 'Vacunación', 'Chequeo general', 'Dermatología', 'Oftalmología',
        'Cardiología', 'Ginecología', 'Urología', 'Pediatría', 'Otorrinolaringología',
        'Medicina interna', 'Endocrinología', 'Nutrición', 'Psicología', 'Psiquiatría',
        'Neumología', 'Fisioterapia', 'Rehabilitación', 'Neurología', 'Revisión postoperatoria',
        'Análisis de laboratorio', 'Control de peso', 'Revisión de medicamentos',
        'Consulta virtual', 'Medicina del deporte'
    ]

    # Obtener especialidades más frecuentes del usuario
    top_specialties = (
        Appointment.objects.filter(user=request.user)
        .values('specialty')
        .annotate(count=Count('specialty'))
        .order_by('-count')
        .values_list('specialty', flat=True)
    )

    frequent = [s for s in top_specialties if s in all_specialties]
    others = [s for s in all_specialties if s not in frequent]

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')  # Redirige a la lista de citas
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/edit_appointment.html', {
        'form': form,
        'frequent': frequent,
        'others': others
    })

# Crea una cita asignándola al usuario autenticado

@login_required
def create_appointment(request):
    user = request.user

    all_specialties = [
        'Odontología', 'Vacunación', 'Chequeo general', 'Dermatología', 'Oftalmología',
        'Cardiología', 'Ginecología', 'Urología', 'Pediatría', 'Otorrinolaringología',
        'Medicina interna', 'Endocrinología', 'Nutrición', 'Psicología', 'Psiquiatría',
        'Neumología', 'Fisioterapia', 'Rehabilitación', 'Neurología', 'Revisión postoperatoria',
        'Análisis de laboratorio', 'Control de peso', 'Revisión de medicamentos',
        'Consulta virtual', 'Medicina del deporte'
    ]

    top_specialties = (
        Appointment.objects.filter(user=user)
        .values('specialty')
        .annotate(count=Count('specialty'))
        .order_by('-count')
        .values_list('specialty', flat=True)
    )

    frequent = [s for s in top_specialties if s in all_specialties]
    others = [s for s in all_specialties if s not in frequent]
    specialty_choices = [(s, s) for s in frequent + others]

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        form.fields['specialty'].choices = specialty_choices

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = user
            appointment.save()
            return redirect('appointment_list')
    else:
        date_str = request.GET.get('date')
        initial_data = {}

        if date_str:
            try:
                # Parseamos DD-MM-YYYY a objeto date
                appointment_date = datetime.strptime(date_str, '%d-%m-%Y').date()
                # Asumamos que el campo de fecha en el form se llama 'date'
                initial_data['date'] = appointment_date
            except ValueError:
                pass  # Fecha inválida, ignoramos

        form = AppointmentForm(initial=initial_data)
        form.fields['specialty'].choices = specialty_choices

    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'frequent': frequent,
        'others': others
    })

# Solo permite eliminar citas del usuario autenticado
@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)  # Verifica que la cita pertenezca al usuario

    if request.method == "POST":
        appointment.delete()
        return redirect('appointment_list')  # Redirige a la lista de citas después de eliminar

    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})

@login_required
def appointment_recommendations(request):
    user_id = request.user.id

    # Obtener el servicio de recomendación usando inyección de dependencias
    recommendation_service = get_recommendation_service()
    
    # Obtener las citas recomendadas para el usuario
    recommended_appointments = recommendation_service.get_recommendations(user_id)

    # Mostrar recomendaciones en el template
    return render(request, 'appointments/recommendations.html', {
        'recommended_appointments': recommended_appointments
    })


color_map = {
    'Odontología': '#4E79A7',
    'Vacunación': '#59A14F',
    'Chequeo general': '#9C755F',
    'Dermatología': '#F28E2B',
    'Oftalmología': '#76B7B2',
    'Cardiología': '#E15759',
    'Ginecología': '#B07AA1',
    'Urología': '#D37295',
    'Pediatría': '#FF9DA7',
    'Otorrinolaringología': '#F1CE63',
    'Medicina interna': '#8CD17D',
    'Endocrinología': '#A0CBE8',
    'Nutrición': '#FFBE7D',
    'Psicología': '#B6992D',
    'Psiquiatría': '#CFCFCF',
    'Neumología': '#79706E',
    'Fisioterapia': '#5F9EA0',
    'Rehabilitación': '#AADEA7',
    'Neurología': '#B07AA1',
    'Revisión postoperatoria': '#D4A6C8',
    'Análisis de laboratorio': '#BAB0AC',
    'Control de peso': '#E17C05',
    'Revisión de medicamentos': '#C44E52',
    'Consulta virtual': '#6B6ECF',
    'Medicina del deporte': '#17BECF',
}

@login_required
def calendar_view(request):
    user_appointments = Appointment.objects.filter(user=request.user)
    events = []

    for appointment in user_appointments:
        events.append({
            'id': appointment.id,
            'title': appointment.specialty,
            'start': appointment.date.isoformat(),
            'color': color_map.get(appointment.specialty, '#7f7f7f'),  # Color en el evento
            'extendedProps': {
                'time': appointment.time.strftime('%H:%M') if appointment.time else 'No definida',
                'address': appointment.address if appointment.address else 'No definida',
                'color': color_map.get(appointment.specialty, '#7f7f7f'),  # Aseguramos que el color esté aquí también
        }
        })


    context = {
        'events_json': json.dumps(events)
    }
    return render(request, 'appointments/calendar.html', context)
