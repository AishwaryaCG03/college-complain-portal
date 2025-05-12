from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from portal.models import Complaint, Profile
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Escalate pending complaints older than 14 days'

    def handle(self, *args, **options):
        now = timezone.now()
        threshold = now - timedelta(days=14)
        pending_complaints = Complaint.objects.filter(status='Pending', created_at__lte=threshold)

        escalation_map = {
            0: 'class_teacher',
            1: 'hod',
            2: 'principal'
        }

        for complaint in pending_complaints:
            current_level = complaint.escalation_level
            if current_level >= 3:
                continue  # max escalation reached
            
            next_level = current_level + 1
            complaint.escalation_level = next_level

            # Find user(s) of next level authority - for example, assume Profile.role stores these roles
            role_str = escalation_map.get(current_level)
            if not role_str:
                continue

            # Assign complaint to first user with that role (customize logic as needed)
            next_authority = Profile.objects.filter(role=role_str).first()
            if next_authority and next_authority.user:
                complaint.assigned_to = next_authority.user
                complaint.save()

                # Send notification email to next authority
                subject = f"Complaint ID {complaint.id} escalated to you"
                message = f"A complaint has been escalated to you for action.\n\nDescription: {complaint.description}\nPlease review it as soon as possible."
                recipient = [next_authority.user.email]

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
                self.stdout.write(f'Escalated complaint {complaint.id} to {role_str}')
            else:
                complaint.save()  # Save escalation level even if no next authority found
                self.stdout.write(f'No user found for role {role_str} to assign complaint {complaint.id}')
