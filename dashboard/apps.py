from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        """Django käynnistyy - QA-ajastin poistettu väliaikaisesti"""
        print("Dashboard ready - QA scheduler temporarily disabled")