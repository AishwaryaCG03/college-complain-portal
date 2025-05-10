from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm, ComplaintForm, RatingForm
from .models import Complaint, Category, Profile
from django.utils import timezone

def send_resolution_email(complaint):
    subject = 'Your Complaint has been Resolved'
    message = f'Your complaint (ID: {complaint.id}) has been resolved. Thank you for your patience!'
    recipient_list = [complaint.user.email] if complaint.user else []
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            profile = Profile.objects.create(user=user, role=role)
            profile.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    role = profile.role
    # Filter complaints based on user and role
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'complaints': complaints,
        'role': role,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
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
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            complaint.rating = rating
            complaint.save()
            messages.success(request, 'Thank you for your rating!')
            return redirect('complaint_detail', pk=pk)
    else:
        form = RatingForm()

    # Check if the complaint is being resolved
    if complaint.status == 'Pending' and request.POST.get('resolve'):
        complaint.status = 'Resolved'
        complaint.resolved_at = timezone.now()
        
        # Send email notification if not already sent
        if not complaint.email_sent:
            send_resolution_email(complaint)
            complaint.email_sent = True  # Mark email as sent

        complaint.save()
        messages.success(request, 'Complaint resolved successfully!')
        return redirect('complaint_detail', pk=pk)
    return render(request, 'portal/complaint_detail.html', {
        'complaint': complaint,
        'form': form,
        'rating_given': rating_given,
    })

@login_required
def profile(request):
    return render(request, 'portal/profile.html')
