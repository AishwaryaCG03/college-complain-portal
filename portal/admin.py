from django.contrib import admin
from .models import Profile, Category, Complaint

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'status', 'created_at', 'resolved_at', 'anonymous', 'escalation_level')
    list_filter = ('status', 'category', 'escalation_level')
    search_fields = ('description',)
