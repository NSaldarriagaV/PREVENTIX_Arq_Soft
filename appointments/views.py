from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from .models import Appointment
from .forms import AppointmentForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from appointments.services.specialties import get_specialty_choices_for_user

ALL_SPECIALTIES = [
    'Odontología', 'Vacunación', 'Chequeo general', 'Dermatología', 'Oftalmología',
    'Cardiología', 'Ginecología', 'Urología', 'Pediatría', 'Otorrinolaringología',
    'Medicina interna', 'Endocrinología', 'Nutrición', 'Psicología', 'Psiquiatría',
    'Neumología', 'Fisioterapia', 'Rehabilitación', 'Neurología', 'Revisión postoperatoria',
    'Análisis de laboratorio', 'Control de peso', 'Revisión de medicamentos',
    'Consulta virtual', 'Medicina del deporte'
]

SPECIALTY_COLORS = {
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
DEFAULT_EVENT_COLOR = '#7f7f7f'

@login_required
def appointment_list(request):
    today = timezone.localdate()  # usa timezone coherente
    upcoming_appointments = Appointment.objects.for_user(request.user).upcoming()
    past_appointments = Appointment.objects.for_user(request.user).past()

    return render(request, 'appointments/list.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, user=request.user)

    specialty_choices, frequent, others = get_specialty_choices_for_user(request.user)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        form.fields['specialty'].choices = specialty_choices
        if form.is_valid():
            try:
                form.save()  # validación final vive en el modelo
                messages.success(request, "Appointment updated successfully.")
                return redirect('appointments:appointment_list')  # o 'appointment_list' si no usas namespace
            except ValidationError as e:
                for field, msgs in e.message_dict.items():
                    for msg in msgs:
                        form.add_error(field if field in form.fields else None, msg)
    else:
        form = AppointmentForm(instance=appointment)
        form.fields['specialty'].choices = specialty_choices  # ✅ también en GET

    return render(request, 'appointments/edit_appointment.html', {
        'form': form,
        'frequent': frequent,
        'others': others,
    })


@login_required
def create_appointment(request):
    user = request.user
    specialty_choices, frequent, others = get_specialty_choices_for_user(user)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        form.fields['specialty'].choices = specialty_choices
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = user
            try:
                appointment.save()  # validación final en modelo
                messages.success(request, "Appointment created successfully.")
                return redirect('appointments:appointment_list')
            except ValidationError as e:
                # Adjunta errores del modelo
                for field, msgs in e.message_dict.items():
                    for msg in msgs:
                        form.add_error(field if field in form.fields else None, msg)
    else:
        date_str = request.GET.get('date')
        initial_data = {}
        if date_str:
            try:
                appointment_date = datetime.strptime(date_str, '%d-%m-%Y').date()
                initial_data['date'] = appointment_date
            except ValueError:
                pass

        form = AppointmentForm(initial=initial_data)
        form.fields['specialty'].choices = specialty_choices

    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'frequent': frequent,
        'others': others
    })

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if request.method == "POST":
        appointment.delete()
        return redirect('appointments:appointment_list')

    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})

@login_required
def calendar_view(request):
    user_appointments = Appointment.objects.filter(user=request.user)
    events = []
    for appointment in user_appointments:
        events.append({
            'id': appointment.id,
            'title': appointment.specialty,
            'start': appointment.date.isoformat(),
            'color': color_map.get(appointment.specialty, '#7f7f7f'),
            'extendedProps': {
                'time': appointment.time.strftime('%H:%M') if appointment.time else 'No definida',
                'address': appointment.address if appointment.address else 'No definida',
                'color': color_map.get(appointment.specialty, '#7f7f7f'),
            }
        })
    context = {'events_json': json.dumps(events, cls=DjangoJSONEncoder)}
    return render(request, 'appointments/calendar.html', context)

def get_specialty_choices_for_user(user):
    # Especialidades más usadas por el usuario
    top_specialties = (
        Appointment.objects.filter(user=user)
        .values('specialty')
        .annotate(count=Count('specialty'))
        .order_by('-count')
        .values_list('specialty', flat=True)
    )
    frequent = [s for s in top_specialties if s in ALL_SPECIALTIES]
    others = [s for s in ALL_SPECIALTIES if s not in frequent]
    ordered = frequent + others
    return [(s, s) for s in ordered], frequent, others

def get_specialty_color(specialty: str) -> str:
    return SPECIALTY_COLORS.get(specialty, DEFAULT_EVENT_COLOR)

@login_required
def calendar_view(request):
    user_appointments = Appointment.objects.filter(user=request.user)
    events = []

    for appt in user_appointments:
        color = get_specialty_color(appt.specialty or '')
        events.append({
            'id': appt.id,
            'title': appt.specialty,
            'start': appt.date.isoformat(),
            'color': color,
            'extendedProps': {
                'time': appt.time.strftime('%H:%M') if appt.time else 'No definida',
                'address': appt.address if appt.address else 'No definida',
                'color': color,
            }
        })

    context = {'events_json': json.dumps(events, cls=DjangoJSONEncoder)}
    return render(request, 'appointments/calendar.html', context)