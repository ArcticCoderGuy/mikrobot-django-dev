"""
U-Cell Integration URLs for Django
URL routing for U-Cell API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .u_cell_views import (
    UCellSignalValidationViewSet,
    UCellRiskAssessmentViewSet,
    UCellExecutionViewSet,
    UCellQualityMeasurementViewSet,
    UCellSystemHealthViewSet,
    UCellStatisticalMonitoringViewSet
)

# Create router for U-Cell ViewSets
router = DefaultRouter()

# Register U-Cell ViewSets
router.register(r'validations', UCellSignalValidationViewSet, basename='ucell-validation')
router.register(r'risk-assessments', UCellRiskAssessmentViewSet, basename='ucell-risk')
router.register(r'executions', UCellExecutionViewSet, basename='ucell-execution')
router.register(r'quality-measurements', UCellQualityMeasurementViewSet, basename='ucell-quality')
router.register(r'system-health', UCellSystemHealthViewSet, basename='ucell-health')
router.register(r'statistical-monitoring', UCellStatisticalMonitoringViewSet, basename='ucell-monitoring')

# U-Cell specific URL patterns
urlpatterns = [
    # Include router URLs with u-cell prefix
    path('u-cell/', include(router.urls)),
    
    # Additional custom endpoints can be added here
    # path('u-cell/integration-status/', UCellIntegrationStatusView.as_view(), name='ucell-integration-status'),
    # path('u-cell/signal-flow/<uuid:signal_id>/', UCellSignalFlowView.as_view(), name='ucell-signal-flow'),
]

# Export router for inclusion in main URLs
u_cell_router = router