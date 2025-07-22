from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from .utils import (
    get_mt5_account_info,
    get_active_trades, 
    get_closed_trades,
    get_recent_signals,
    get_system_status,
    get_weekly_performance,
    get_notifications,
    get_process_flow
)


def dashboard_view(request):
    """
    Main dashboard view that displays the MikroBot trading dashboard
    Integrates real data functions with fallback to mock data
    """
    try:
        # Get user settings for dashboard display
        from core.models import UserSettings
        
        if request.user.is_authenticated:
            user_settings, created = UserSettings.objects.get_or_create(
                user=request.user,
                defaults={'currency_pair': 'EURUSD', 'risk_percentage': 1.0}
            )
            current_settings = {
                'currency_pair': user_settings.currency_pair,
                'risk_percentage': float(user_settings.risk_percentage),
                'stop_loss_level': float(user_settings.stop_loss_level),
                'weekly_profit_threshold': float(user_settings.weekly_profit_threshold),
                'break_even_buffer_pips': float(user_settings.break_even_buffer_pips),
                'trade_london': user_settings.trade_london,
                'trade_new_york': user_settings.trade_new_york,
                'trade_tokyo': user_settings.trade_tokyo,
                'notification_email': user_settings.notification_email or '',
                'notification_email_enabled': user_settings.notification_email_enabled,
                'metaquotes_id': user_settings.metaquotes_id or '',
                'metaquotes_enabled': user_settings.metaquotes_enabled,
                'telegram_username': user_settings.telegram_username or '',
                'telegram_enabled': user_settings.telegram_enabled,
                'sms_phone': user_settings.sms_phone or '',
                'sms_enabled': user_settings.sms_enabled,
                'notification_email': user_settings.notification_email or '',
                'notification_email_enabled': user_settings.notification_email_enabled,
                'metaquotes_id': user_settings.metaquotes_id or '',
                'metaquotes_enabled': user_settings.metaquotes_enabled,
                'telegram_username': user_settings.telegram_username or '',
                'telegram_enabled': user_settings.telegram_enabled,
                'sms_phone': user_settings.sms_phone or '',
                'sms_enabled': user_settings.sms_enabled,
                'adx_value': 27  # Mock ADX value - will be replaced with real data later
            }
        else:
            # For anonymous users, use session
            current_settings = {
                'currency_pair': request.session.get('currency_pair', 'EURUSD'),
                'risk_percentage': request.session.get('risk_percentage', 1.0),
                'stop_loss_level': request.session.get('stop_loss_level', 0.28),
                'weekly_profit_threshold': request.session.get('weekly_profit_threshold', 10.0),
                'break_even_buffer_pips': request.session.get('break_even_buffer_pips', 2.0),
                'trade_london': request.session.get('trade_london', False),  # London nyt OFF 
                'trade_new_york': request.session.get('trade_new_york', True),   # NY ON
                'trade_tokyo': request.session.get('trade_tokyo', True),        # Tokyo ON (testasit tämän)
                'notification_email': request.session.get('notification_email', ''),
                'notification_email_enabled': request.session.get('notification_email_enabled', True),
                'metaquotes_id': request.session.get('metaquotes_id', ''),
                'metaquotes_enabled': request.session.get('metaquotes_enabled', False),
                'telegram_username': request.session.get('telegram_username', ''),
                'telegram_enabled': request.session.get('telegram_enabled', False),
                'sms_phone': request.session.get('sms_phone', ''),
                'sms_enabled': request.session.get('sms_enabled', False),
                'adx_value': 27  # Mock ADX value for anonymous users
            }
        
        # Attempt to get real data (will fall back to mock data in utils.py)
        account_info = get_mt5_account_info()
        weekly_performance = get_weekly_performance()
        
        # Combine account info with weekly performance
        account_info['weekly_performance'] = weekly_performance
        
        context = {
            'account_info': account_info,
            'system_status': get_system_status(),
            'user_settings': current_settings,
            'trades': get_active_trades(),
            'closed_trades': get_closed_trades(),
            'signals': get_recent_signals(),
            'notifications': get_notifications()
        }
        
        return render(request, 'dashboard/dashboard.html', context)
        
    except Exception as e:
        # Fallback to basic mock data if everything fails
        context = {
            'account_info': {
                'balance': 0.00,
                'equity': 0.00,
                'margin': 0.00,
                'free_margin': 0.00,
                'profit': 0.00,
                'weekly_performance': {},
                'error': 'Data unavailable'
            },
            'system_status': {
                'django': True,
                'mt5': False,
                'mcp': False,
                'llm': False,
                'pure_ea': False,
                'timeframe_sync': False,
                'error': str(e)
            },
            'user_settings': {
                'currency_pair': 'EURUSD',
                'risk_percentage': 1.0,
                'stop_loss_level': 0.28,
                'weekly_profit_threshold': 10.0,
                'break_even_buffer_pips': 2.0,
                'trade_london': True,
                'trade_new_york': True,
                'trade_tokyo': False,
                'notification_email': '',
                'notification_email_enabled': True,
                'metaquotes_id': '',
                'metaquotes_enabled': False,
                'telegram_username': '',
                'telegram_enabled': False,
                'sms_phone': '',
                'sms_enabled': False,
                'adx_value': 24  # Mock ADX value for error fallback (shows red)
            },
            'trades': [],
            'signals': [],
            'notifications': []
        }
        
        return render(request, 'dashboard/dashboard.html', context)


def qa_dashboard_view(request):
    """
    QA Dashboard for testing and development
    """
    return render(request, 'dashboard/qa_dashboard.html')


def run_qa_tests_manual(request):
    """
    Aja QA-testit manuaalisesti
    """
    try:
        from .qa_scheduler import qa_scheduler
        qa_scheduler._run_qa_tests()
        
        from django.contrib import messages
        messages.success(request, 'QA tests started! Results will be available in a few seconds.')
        
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Failed to start QA tests: {e}')
    
    return redirect('dashboard:index')


def settings_view(request):
    """
    Settings view for dashboard configuration
    """
    from django.contrib import messages
    from core.models import UserSettings
    
    # Handle anonymous users - use session-based settings
    if request.user.is_authenticated:
        # Get or create user settings
        user_settings, created = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={
                'currency_pair': 'EURUSD', 
                'risk_percentage': 1.0, 
                'stop_loss_level': 0.28,
                'weekly_profit_threshold': 10.0,
                'break_even_buffer_pips': 2.0,
                'trade_london': True,
                'trade_new_york': True,
                'trade_tokyo': False
            }
        )
    else:
        # For anonymous users, use session
        user_settings = type('obj', (object,), {
            'currency_pair': request.session.get('currency_pair', 'EURUSD'),
            'risk_percentage': request.session.get('risk_percentage', 1.0),
            'stop_loss_level': request.session.get('stop_loss_level', 0.28),
            'weekly_profit_threshold': request.session.get('weekly_profit_threshold', 10.0),
            'break_even_buffer_pips': request.session.get('break_even_buffer_pips', 2.0),
            'trade_london': request.session.get('trade_london', True),
            'trade_new_york': request.session.get('trade_new_york', True),
            'trade_tokyo': request.session.get('trade_tokyo', False),
            'notification_email': request.session.get('notification_email', ''),
            'notification_email_enabled': request.session.get('notification_email_enabled', True),
            'metaquotes_id': request.session.get('metaquotes_id', ''),
            'metaquotes_enabled': request.session.get('metaquotes_enabled', False),
            'telegram_username': request.session.get('telegram_username', ''),
            'telegram_enabled': request.session.get('telegram_enabled', False),
            'sms_phone': request.session.get('sms_phone', ''),
            'sms_enabled': request.session.get('sms_enabled', False)
        })
    
    if request.method == 'POST':
        # Handle form submission
        currency_pair = request.POST.get('currency_pair', 'EURUSD')
        risk_percentage = request.POST.get('risk_percentage', '1.0')
        stop_loss_level = request.POST.get('stop_loss_level', '0.28')
        weekly_profit_threshold = request.POST.get('weekly_profit_threshold', '10.0')
        break_even_buffer_pips = request.POST.get('break_even_buffer_pips', '2.0')
        # Trading sessions
        trade_london = 'trade_london' in request.POST
        trade_new_york = 'trade_new_york' in request.POST
        trade_tokyo = 'trade_tokyo' in request.POST
        
        # Notifications
        notification_email = request.POST.get('notification_email', '')
        notification_email_enabled = 'notification_email_enabled' in request.POST
        metaquotes_id = request.POST.get('metaquotes_id', '')
        metaquotes_enabled = 'metaquotes_enabled' in request.POST
        telegram_username = request.POST.get('telegram_username', '')
        telegram_enabled = 'telegram_enabled' in request.POST
        sms_phone = request.POST.get('sms_phone', '')
        sms_enabled = 'sms_enabled' in request.POST
        
        try:
            if request.user.is_authenticated:
                # Update settings in database
                user_settings.currency_pair = currency_pair
                user_settings.risk_percentage = float(risk_percentage)
                user_settings.stop_loss_level = float(stop_loss_level)
                user_settings.weekly_profit_threshold = float(weekly_profit_threshold)
                user_settings.break_even_buffer_pips = float(break_even_buffer_pips)
                user_settings.trade_london = trade_london
                user_settings.trade_new_york = trade_new_york
                user_settings.trade_tokyo = trade_tokyo
                user_settings.notification_email = notification_email if notification_email else None
                user_settings.notification_email_enabled = notification_email_enabled
                user_settings.metaquotes_id = metaquotes_id if metaquotes_id else None
                user_settings.metaquotes_enabled = metaquotes_enabled
                user_settings.telegram_username = telegram_username if telegram_username else None
                user_settings.telegram_enabled = telegram_enabled
                user_settings.sms_phone = sms_phone if sms_phone else None
                user_settings.sms_enabled = sms_enabled
                user_settings.save()
            else:
                # Update session for anonymous users
                request.session['currency_pair'] = currency_pair
                request.session['risk_percentage'] = float(risk_percentage)
                request.session['stop_loss_level'] = float(stop_loss_level)
                request.session['weekly_profit_threshold'] = float(weekly_profit_threshold)
                request.session['break_even_buffer_pips'] = float(break_even_buffer_pips)
                request.session['trade_london'] = trade_london
                request.session['trade_new_york'] = trade_new_york
                request.session['trade_tokyo'] = trade_tokyo
                request.session['notification_email'] = notification_email
                request.session['notification_email_enabled'] = notification_email_enabled
                request.session['metaquotes_id'] = metaquotes_id
                request.session['metaquotes_enabled'] = metaquotes_enabled
                request.session['telegram_username'] = telegram_username
                request.session['telegram_enabled'] = telegram_enabled
                request.session['sms_phone'] = sms_phone
                request.session['sms_enabled'] = sms_enabled
            
            messages.success(request, 'Settings saved successfully!')
            return redirect('dashboard:settings')
        except ValueError:
            messages.error(request, 'Invalid risk percentage value')
    
    context = {
        'current_symbol': user_settings.currency_pair,
        'risk_percentage': float(user_settings.risk_percentage),
        'stop_loss_level': float(user_settings.stop_loss_level),
        'weekly_profit_threshold': float(user_settings.weekly_profit_threshold),
        'break_even_buffer_pips': float(user_settings.break_even_buffer_pips),
        'trade_london': user_settings.trade_london,
        'trade_new_york': user_settings.trade_new_york,
        'trade_tokyo': user_settings.trade_tokyo,
        'notification_email': user_settings.notification_email or '',
        'notification_email_enabled': user_settings.notification_email_enabled,
        'metaquotes_id': user_settings.metaquotes_id or '',
        'metaquotes_enabled': user_settings.metaquotes_enabled,
        'telegram_username': user_settings.telegram_username or '',
        'telegram_enabled': user_settings.telegram_enabled,
        'sms_phone': user_settings.sms_phone or '',
        'sms_enabled': user_settings.sms_enabled,
        'available_symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD'],
        'risk_options': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        'stop_loss_options': [0.15, 0.28, 0.50, 0.63],
        'weekly_threshold_options': [5.0, 7.5, 10.0, 12.5, 15.0],
        'buffer_pips_options': [1.0, 1.5, 2.0, 2.5, 3.0]
    }
    return render(request, 'dashboard/settings.html', context)


def index_view(request):
    """
    Main index/welcome page with system overview
    """
    try:
        # Import here to avoid circular imports
        from signals.models import MQL5Signal
        from trading.models import Trade
        
        # Get basic stats
        signals_count = MQL5Signal.objects.count()
        trades_count = Trade.objects.count()
        signals_today = MQL5Signal.objects.filter(received_at__date=datetime.now().date()).count()
        active_trades_count = Trade.objects.filter(status='opened').count()
        
        # Get basic settings for display
        if request.user.is_authenticated:
            from core.models import UserSettings
            user_settings, created = UserSettings.objects.get_or_create(
                user=request.user,
                defaults={'currency_pair': 'EURUSD', 'risk_percentage': 1.0}
            )
            current_settings = {
                'currency_pair': user_settings.currency_pair,
                'risk_percentage': float(user_settings.risk_percentage),
            }
        else:
            current_settings = {
                'currency_pair': request.session.get('currency_pair', 'EURUSD'),
                'risk_percentage': request.session.get('risk_percentage', 1.0),
            }
        
        # Import QA status
        try:
            from .qa_status import get_qa_status_summary
            qa_status = get_qa_status_summary()
        except Exception:
            qa_status = {'status': 'ERROR', 'message': 'QA status unavailable'}
        
        context = {
            'signals_count': signals_count,
            'trades_count': trades_count,
            'signals_today': signals_today,
            'active_trades_count': active_trades_count,
            'user_settings': current_settings,
            'system_status': get_system_status(),
            'account_info': get_mt5_account_info(),
            'qa_status': qa_status,
        }
        
        return render(request, 'dashboard/index.html', context)
        
    except Exception as e:
        # Fallback context
        context = {
            'signals_count': 3,
            'trades_count': 1,
            'signals_today': 0,
            'active_trades_count': 1,
            'user_settings': {'currency_pair': 'EURUSD', 'risk_percentage': 1.0},
            'system_status': {'mt5': False, 'pure_ea': False, 'llm': False, 'mcp': False},
            'account_info': {'balance': '100,000 (Demo)'},
            'error': str(e)
        }
        return render(request, 'dashboard/index.html', context)


def hello_dashboard(request):
    """
    Simple test view to verify Django integration
    """
    return JsonResponse({
        'message': 'Hello Dashboard - MikroBot Django Integration Working!',
        'status': 'success',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


def new_design_preview(request):
    """
    Preview of the new glassmorphism design
    """
    return render(request, 'new_design_preview.html')


def functional_design(request):
    """
    Functional trading dashboard with glassmorphism design
    """
    return render(request, 'functional_design.html')