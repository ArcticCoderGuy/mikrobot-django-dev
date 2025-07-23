from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, webhooks
from .discord_webhook import discord_webhook
from .pure_ea_webhook import pure_ea_webhook
from . import u_cell_urls

router = DefaultRouter()
router.register(r'signals', views.MQL5SignalViewSet)

urlpatterns = [
    # API endpoints
    path('api/v1/', include(router.urls)),
    
    # U-Cell Integration API endpoints
    path('api/v1/', include(u_cell_urls.urlpatterns)),
    
    # Webhook endpoints for PURE Signal Detector
    path('api/v1/pure-signal/', webhooks.pure_signal_webhook, name='pure_signal_webhook'),
    path('api/v1/pure-signal/status/', webhooks.pure_signal_status, name='pure_signal_status'),
    path('api/v1/pure-signal/timeframes/', webhooks.pure_timeframe_webhook, name='pure_timeframe_webhook'),
    path('api/v1/llm-approval/', webhooks.llm_approval_webhook, name='llm_approval_webhook'),
    
    # Alternative class-based webhook (if needed)
    path('webhook/pure-signal/', webhooks.PureSignalWebhookView.as_view(), name='pure_signal_webhook_class'),
    
    # Discord webhook endpoint
    path('discord-webhook/', discord_webhook, name='discord_webhook'),
    
    # PURE EA webhook endpoint (BOS signals)
    path('api/signals/receive/', pure_ea_webhook, name='pure_ea_webhook'),
]