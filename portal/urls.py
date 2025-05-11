from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
   
    path('complaint/new/', views.create_complaint, name='create_complaint'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('profile/', views.profile, name='profile'),
]
