from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portal import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),  
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/verify-code/', views.password_reset_verify_code_view, name='password_reset_verify_code'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
