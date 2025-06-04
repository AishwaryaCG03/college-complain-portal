from django.core.management.base import BaseCommand
from complaintportal.models import Complaint

class Command(BaseCommand):
    help = "Auto escalate overdue complaints and notify responsible users via email"

    def handle(self, *args, **options):
        complaints = Complaint.objects.filter(status__in=['Pending', 'Escalated'])
        count = 0
        for complaint in complaints:
            old_level = complaint.escalation_level
            complaint.auto_escalate_and_notify()
            if complaint.escalation_level > old_level:
                count += 1

        self.stdout.write(f"Escalated and emailed notifications for {count} complaints")
