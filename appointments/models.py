from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class AppointmentQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def upcoming(self):
        today = timezone.localdate()
        return self.filter(date__gte=today).order_by('date', 'time')

    def past(self):
        today = timezone.localdate()
        return self.filter(date__lt=today).order_by('-date', '-time')


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    specialty = models.CharField(max_length=255)
    doctor_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)

    objects = AppointmentQuerySet.as_manager()

    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"

    # --- Fat Model: lógica de negocio/validación aquí ---
    def is_overlapping(self) -> bool:
        """
        Colisión = ya existe otra cita del mismo usuario exactamente en la misma fecha+hora.
        (Como no tenemos duración, usamos igualdad estricta.)
        """
        return Appointment.objects.for_user(self.user).exclude(pk=self.pk).filter(
            date=self.date,
            time=self.time,
        ).exists()

    def clean(self):
        # 1) Fecha en el pasado
        today = timezone.localdate()
        if self.date < today:
            raise ValidationError({"date": "The appointment date cannot be in the past."})

        # 2) Solapamiento
        if self.user_id and self.date and self.time and self.is_overlapping():
            raise ValidationError({
                "time": "You already have an appointment at this date and time."
            })

        # 3) Validaciones opcionales (dirección/doctor)
        if not self.doctor_name.strip():
            raise ValidationError({"doctor_name": "Doctor name is required."})
        if not self.address.strip():
            raise ValidationError({"address": "Address is required."})

    def save(self, *args, **kwargs):
        # Garantiza que siempre se valide al guardar
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["date", "time"]),
        ]
        constraints = [
            # Refuerzo de unicidad por usuario-fecha-hora (nivel DB)
            models.UniqueConstraint(
                fields=["user", "date", "time"],
                name="uniq_user_date_time"
            )
        ]
        ordering = ["date", "time"]

    def clean(self):
        errors = {}

        if not self.date:
            errors['date'] = "Date is required."
        if not self.time:
            errors['time'] = "Time is required."
        if not self.doctor_name or not self.doctor_name.strip():
            errors['doctor_name'] = "Doctor name is required."
        if not self.address or not self.address.strip():
            errors['address'] = "Address is required."

        if errors:
         
            raise ValidationError(errors)
        
        today = timezone.localdate()
        if self.date < today:
            raise ValidationError({'date': 'The appointment date cannot be in the past.'})

        if self.user_id and self.is_overlapping():
            raise ValidationError({'time': 'You already have an appointment at this date and time.'})   
