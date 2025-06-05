from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm, ComplaintForm, RatingForm, PasswordResetRequestForm, PasswordResetCodeForm, SetNewPasswordForm
from .models import Complaint, Category, Profile, PasswordResetCode
from django.utils import timezone
from django.db.models import Count, Avg
from datetime import timedelta
from textblob import TextBlob  
import random
from django.contrib.auth.models import User

def send_resolution_email(complaint):
    subject = 'Your Complaint has been Resolved'
    message = f'Your complaint (ID: {complaint.id}) has been resolved. Thank you for your patience!'
    recipient_list = [complaint.user.email] if complaint.user else []
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_password_reset_email(user, code):
    subject = 'Password Reset Request'
    message = f'Hi {user.username},\n\nYou requested a password reset. Your code is: {code}\nThis code will expire in 15 minutes.\nThank you!'
    recipient_list = [user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    role = profile.role

    if role in ['student', 'faculty', 'non_teaching', 'worker']:
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    elif role in ['class_teacher', 'hod', 'principal']:
        complaints = Complaint.objects.filter(assigned_to=request.user).order_by('-created_at')
    else:
        complaints = Complaint.objects.all().order_by('-created_at')

    # Prepare data for charts and stats
    categories = Category.objects.all()
    category_labels = [cat.name for cat in categories]
    category_counts = [complaints.filter(category=cat).count() for cat in categories]

    status_choices = ['Pending', 'Escalated', 'Resolved']
    status_counts = [complaints.filter(status=status).count() for status in status_choices]

    total_complaints = complaints.count()
    resolved_count = complaints.filter(status='Resolved').count()
    resolved_rate = (resolved_count / total_complaints * 100) if total_complaints else 0
    avg_rating = complaints.aggregate(avg=Avg('rating'))['avg'] or 0

    escalation_count = Complaint.objects.filter(status='Escalated').count() if role == 'admin' else 0
    overdue_count = 0
    if role == 'admin':
        overdue_count = Complaint.objects.filter(
            status__in=['Pending', 'Escalated'],
            created_at__lte=timezone.now() - timedelta(days=14)
        ).count()

    context = {
        'complaints': complaints,
        'role': role,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'status_labels': status_choices,
        'status_counts': status_counts,
        'total_complaints': total_complaints,
        'resolved_count': resolved_count,
        'resolved_rate': round(resolved_rate, 2),
        'avg_rating': round(avg_rating, 2),
        'escalation_count': escalation_count,
        'overdue_count': overdue_count,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            analysis = TextBlob(complaint.description)
            complaint.sentiment = analysis.sentiment.polarity
            anonymous = form.cleaned_data.get('anonymous')
            if anonymous:
                complaint.anonymous = True
                complaint.user = None
            else:
                complaint.user = request.user
                complaint.anonymous = False
            complaint.save()
            messages.success(request, 'Complaint submitted successfully')
            return redirect('dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'portal/complaint_create.html', {'form': form})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    rating_given = complaint.rating is not None

    if request.method == 'POST':
        if 'resolve' in request.POST:
            complaint.status = 'Resolved'
            complaint.resolved_at = timezone.now()
            if not complaint.email_sent:
                send_resolution_email(complaint)
                complaint.email_sent = True
            complaint.save()
            messages.success(request, 'Complaint marked as resolved.')
            return redirect('complaint_detail', pk=pk)
        else:
            form = RatingForm(request.POST)
            if form.is_valid():
                complaint.rating = form.cleaned_data['rating']
                complaint.save()
                messages.success(request, 'Thank you for your rating!')
                return redirect('complaint_detail', pk=pk)
    else:
        form = RatingForm()

    return render(request, 'portal/complaint_detail.html', {
        'complaint': complaint,
        'form': form,
        'rating_given': rating_given,
    })

@login_required
def profile(request):
    return render(request, 'portal/profile.html')

# Password Reset Views
def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generate 4 digit code
            code = f"{random.randint(1000, 9999)}"

            # Delete any existing code for user
            PasswordResetCode.objects.filter(user=user).delete()

            # Save new code
            PasswordResetCode.objects.create(user=user, code=code)

            # Send email
            send_password_reset_email(user, code)

            request.session['password_reset_user_id'] = user.id  # Save in session for next steps

            messages.success(request, '4-digit code has been sent to your email.')
            return redirect('password_reset_verify_code')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'portal/password_reset_request.html', {'form': form})

def password_reset_verify_code_view(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        messages.error(request, "Please enter your email to reset password first.")
        return redirect('password_reset_request')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code_entered = form.cleaned_data['code']
            try:
                reset_code = PasswordResetCode.objects.get(user=user)
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'No reset code found. Please request a new one.')
                return redirect('password_reset_request')

            if reset_code.is_expired():
                reset_code.delete()
                messages.error(request, "Code expired. Please request a new one.")
                return redirect('password_reset_request')

            if reset_code.code != code_entered:
                messages.error(request, "Invalid code entered. Please try again.")
                return redirect('password_reset_verify_code')

            # Code is valid - Proceed to password reset
            request.session['password_reset_verified'] = True
            return redirect('password_reset_confirm')
    else:
        form = PasswordResetCodeForm()
    return render(request, 'portal/password_reset_verify_code.html', {'form': form})

def password_reset_confirm_view(request):
    user_id = request.session.get('password_reset_user_id')
    verified = request.session.get('password_reset_verified', False)

    if not user_id or not verified:
        messages.error(request, "Unauthorized access or session expired. Please start over.")
        return redirect('password_reset_request')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Cleanup session and reset code
            request.session.pop('password_reset_user_id', None)
            request.session.pop('password_reset_verified', None)
            PasswordResetCode.objects.filter(user=user).delete()

            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect('login')
    else:
        form = SetNewPasswordForm(user)
    return render(request, 'portal/password_reset_confirm.html', {'form': form})
