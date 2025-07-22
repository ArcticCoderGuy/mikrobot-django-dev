from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'trades', views.TradeViewSet)
router.register(r'sessions', views.TradingSessionViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]