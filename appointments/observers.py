from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """React to event with data."""
        raise NotImplementedError

class Subject(ABC):
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, data: Dict[str, Any]) -> None:
        for obs in list(self._observers):
            obs.update(event, data)

# ----- Concrete Observers -----

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model

class EmailReminderObserver(Observer):
    def update(self, event: str, data: Dict[str, Any]) -> None:
        if event != "appointment.reminder_due":
            return
        user = data["user"]
        appt = data["appointment"]
        subject = render_to_string(
            "appointments/notifications/email/appointment_reminder_subject.txt",
            {"appointment": appt, "user": user}
        ).strip()
        body = render_to_string(
            "appointments/notifications/email/appointment_reminder.txt",
            {"appointment": appt, "user": user}
        )
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@preventix.local"),
            [user.email],
            fail_silently=True,
        )

class InAppReminderObserver(Observer):
    """Ejemplo: registra el recordatorio en una tabla de notificaciones internas."""
    def update(self, event: str, data: Dict[str, Any]) -> None:
        if event != "appointment.reminder_due":
            return
        from .models import NotificationLog  # import local para evitar ciclos
        user = data["user"]
        appt = data["appointment"]
        NotificationLog.objects.create(
            user=user,
            appointment=appt,
            channel="in_app",
            message=f"Reminder: {appt.title} on {appt.date} at {appt.time}",
        )

class SMSReminderObserver(Observer):
    """Placeholder (futuro Twilio/otro)."""
    def update(self, event: str, data: Dict[str, Any]) -> None:
        if event != "appointment.reminder_due":
            return
        # Integración futura: enviar SMS usando proveedor externo
        return

# ----- Concrete Subject -----

class AppointmentReminderSubject(Subject):
    """Subject que emite el evento cuando hay un recordatorio 'due'."""
    pass
