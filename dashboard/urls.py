from django.urls import path
from . import views, api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('main/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('qa/', views.qa_dashboard_view, name='qa_dashboard'),
    path('hello/', views.hello_dashboard, name='hello_dashboard'),
    path('new-design/', views.new_design_preview, name='new_design_preview'),
    path('functional-design/', views.functional_design, name='functional_design'),
    path('run-qa-tests/', views.run_qa_tests_manual, name='run_qa_tests'),
    
    # API endpoints for real-time data
    path('api/live-trades/', api_views.live_trades_api, name='live_trades_api'),
    path('api/live-account/', api_views.live_account_api, name='live_account_api'),
    path('api/live-data/', api_views.live_all_data_api, name='live_data_api'),
]