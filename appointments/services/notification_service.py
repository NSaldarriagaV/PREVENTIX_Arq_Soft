from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from ..models import Appointment, UserNotificationPreference
from ..observers import (
    AppointmentReminderSubject,
    EmailReminderObserver,
    InAppReminderObserver,
    SMSReminderObserver,
)

def get_subject_for_user(user) -> AppointmentReminderSubject:
    """Crea un Subject y adjunta observers según preferencias del usuario."""
    subject = AppointmentReminderSubject()
    try:
        prefs = UserNotificationPreference.objects.get(user=user)
    except UserNotificationPreference.DoesNotExist:
        prefs = None

    if not prefs or prefs.email_enabled:
        subject.attach(EmailReminderObserver())
    if not prefs or prefs.in_app_enabled:
        subject.attach(InAppReminderObserver())
    if prefs and prefs.sms_enabled:
        subject.attach(SMSReminderObserver())

    return subject

def get_offsets_for_user(user) -> list[int]:
    """Retorna offsets (minutos) para el usuario (default: 24h y 1h)."""
    try:
        prefs = UserNotificationPreference.objects.get(user=user)
        if prefs.offsets_minutes:
            return [int(x) for x in prefs.offsets_minutes]
    except UserNotificationPreference.DoesNotExist:
        pass
    return [1440, 60]  # por defecto: 24h y 1h

def emit_due_reminders(now: datetime | None = None) -> int:
    """
    Busca citas próximas y emite eventos 'appointment.reminder_due'
    cuando coincide la ventana de recordatorio. Retorna # de notificaciones emitidas.
    """
    now = now or timezone.now()
    today = now.date()

    # Citas desde hoy en adelante (no pasadas)
    qs = Appointment.objects.filter(date__gte=today)

    emitted = 0
    for appt in qs.select_related("user"):
        # construir datetime de la cita (date + time)
        if not appt.time:
            continue
        appt_dt = timezone.make_aware(datetime.combine(appt.date, appt.time), timezone.get_current_timezone())

        # si ya pasó, omite
        if appt_dt <= now:
            continue

        # offsets del usuario
        offsets = get_offsets_for_user(appt.user)
        for minutes in offsets:
            target_dt = appt_dt - timedelta(minutes=minutes)

            # considerar ventana de 59 segundos para cron por minuto
            if abs((now - target_dt).total_seconds()) <= 59:
                subject = get_subject_for_user(appt.user)
                subject.notify("appointment.reminder_due", {"user": appt.user, "appointment": appt})
                emitted += 1

    return emitted
