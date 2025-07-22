from django.contrib import admin
from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency_pair', 'risk_percentage', 'updated_at']
    list_filter = ['currency_pair', 'updated_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['-updated_at']
