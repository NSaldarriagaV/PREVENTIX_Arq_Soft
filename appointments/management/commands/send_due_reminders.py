from django.core.management.base import BaseCommand
from ...services.notification_service import emit_due_reminders

class Command(BaseCommand):
    help = "Emite recordatorios de citas 'due' (para ejecuciones por cron)."

    def handle(self, *args, **options):
        count = emit_due_reminders()
        self.stdout.write(self.style.SUCCESS(f"Reminders emitted: {count}"))
