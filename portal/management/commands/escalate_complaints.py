from django.core.management.base import BaseCommand
from portal.models import Complaint
from django.utils import timezone

class Command(BaseCommand):
    help = 'Escalate complaints that are pending and older than 14 days'

    def handle(self, *args, **kwargs):
        pending_complaints = Complaint.objects.filter(status='Pending')
        now = timezone.now()
        escalated_count = 0

        for complaint in pending_complaints:
            days_old = (now - complaint.created_at).days
            if days_old > 14:
                if complaint.escalation_level < 3:
                    complaint.escalate()
                    escalated_count += 1
                    self.stdout.write(f'Escalated Complaint ID {complaint.id} to level {complaint.escalation_level}')
                else:
                    self.stdout.write(f'Complaint ID {complaint.id} already escalated to max level')

        self.stdout.write(self.style.SUCCESS(f'Escalation process completed. {escalated_count} complaints escalated.'))
