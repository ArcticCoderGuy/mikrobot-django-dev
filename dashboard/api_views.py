"""
Real-time API endpoints for dashboard data
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import get_active_trades, get_mt5_account_info, get_sts_signals
import json

@csrf_exempt
def live_trades_api(request):
    """
    API endpoint for live trade data
    Returns current MT5 positions with real-time P&L
    """
    try:
        trades = get_active_trades()
        return JsonResponse({
            'success': True,
            'trades': trades,
            'timestamp': int(__import__('time').time())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def live_account_api(request):
    """
    API endpoint for live account information
    """
    try:
        account_info = get_mt5_account_info()
        return JsonResponse({
            'success': True,
            'account': account_info,
            'timestamp': int(__import__('time').time())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def live_all_data_api(request):
    """
    Combined API endpoint for all dashboard data
    """
    try:
        trades = get_active_trades()
        account_info = get_mt5_account_info()
        sts_signals = get_sts_signals()
        
        return JsonResponse({
            'success': True,
            'data': {
                'trades': trades,
                'account': account_info,
                'sts_signals': sts_signals,
                'timestamp': int(__import__('time').time())
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)