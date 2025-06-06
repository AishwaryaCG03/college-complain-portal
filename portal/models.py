from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

class Profile(models.Model):
    USER_ROLES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('non_teaching', 'Non Teaching Faculty'),
        ('worker', 'Worker'),
        ('guest', 'Guest'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Include country code e.g. +1234567890")

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.role}"
        return f"Guest - {self.role}"

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Complaint(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    anonymous = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    evidence = models.FileField(upload_to='evidence/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'),
        ('Escalated', 'Escalated'),
        ('Resolved', 'Resolved'),
    ), default='Pending')
    rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    escalation_level = models.PositiveIntegerField(default=0)  # 0: initial, 1: class teacher, 2: HOD, 3: Principal
    email_sent = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_complaints')

    def is_overdue(self):
        if self.status != 'Resolved' and (timezone.now() - self.created_at).days > 14:
            return True
        return False

    def auto_escalate_and_notify(self):
        days_open = (timezone.now() - self.created_at).days
        if self.status in ['Pending', 'Escalated'] and days_open > 7 and self.escalation_level < 3:
            self.escalation_level += 1
            self.status = 'Escalated'
            self.save()

            # Determine the user to notify based on escalation level
            notify_user = None
            if self.escalation_level == 1:
                notify_user = self.assigned_to  # Example: class teacher or assigned staff
            elif self.escalation_level == 2:
                # Replace with your HOD retrieval logic
                from .models import Profile
                hod_profile = Profile.objects.filter(role='hod').first()
                if hod_profile:
                    notify_user = hod_profile.user
            elif self.escalation_level == 3:
                # Replace with your Principal retrieval logic
                from .models import Profile
                principal_profile = Profile.objects.filter(role='principal').first()
                if principal_profile:
                    notify_user = principal_profile.user

            if notify_user and notify_user.email:
                subject = f"Complaint ID {self.id} Escalated to Level {self.escalation_level}"
                message = (
                    f"Dear {notify_user.username},\n\n"
                    f"The complaint with ID {self.id} has been escalated to level {self.escalation_level}.\n"
                    f"Please take necessary action.\n\n"
                    "Regards,\n"
                    "College Complaint Portal"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [notify_user.email])

    def __str__(self):
        return f"Complaint {self.id} - {self.category.name} - {self.status}"

@receiver(post_save, sender=User )
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User )
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

# New model for password reset code
class PasswordResetCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_code')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)  # code valid for 15 minutes

    def __str__(self):
        return f"Password reset code for {self.user.email}"
