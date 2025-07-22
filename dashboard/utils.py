"""
Utility functions for dashboard data handling and real data integration
"""
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def get_mt5_account_info():
    """
    Fetch MT5 account information
    Integrates with real MT5 connection when available
    """
    try:
        # Try to get real MT5 data
        from trading.mt5_executor import MT5Executor
        
        executor = MT5Executor()
        if executor.connect():
            account_info = executor.get_account_info()
            if account_info:
                return {
                    'balance': float(account_info.balance),
                    'equity': float(account_info.equity),
                    'margin': float(account_info.margin),
                    'free_margin': float(account_info.margin_free),
                    'margin_level': float(account_info.margin_level),
                    'profit': float(account_info.profit)
                }
    except Exception as e:
        logger.warning(f"Failed to get real MT5 data: {e}")
    
    # Fallback to mock data
    return {
        'balance': 10000.00,
        'equity': 10245.67,
        'margin': 150.00,
        'free_margin': 10095.67,
        'margin_level': 6830.45,
        'profit': 245.67,
        'source': 'mock'
    }


def get_active_trades():
    """
    Fetch active trades from MT5 LIVE
    Shows ALL positions currently open in MT5
    """
    try:
        # Import here to avoid circular imports
        from .mt5_sync import get_mt5_live_trades
        
        # Get live trades from MT5
        mt5_trades = get_mt5_live_trades()
        
        # Convert to dashboard format
        formatted_trades = []
        for trade in mt5_trades:
            formatted_trades.append({
                'id': trade['id'],
                'symbol': trade['symbol'],
                'type': trade['type'],
                'volume': trade['volume'],
                'open_price': trade['open_price'],
                'current_price': trade['current_price'],
                'stop_loss': trade['stop_loss'],
                'take_profit': trade['take_profit'],
                'profit': trade['profit'],
                'profit_pips': trade['profit_pips'],
                'status': trade['status'],
                'open_time': trade['open_time'],
                'comment': trade.get('comment', ''),
                'source': 'MT5',
                'timeframe': 'LIVE',
                'rr_strategy': '1:1',
                'break_even': None,
                'weekly_pnl': 0.0
            })
        
        return formatted_trades
            
    except Exception as e:
        logger.warning(f"Failed to get MT5 trades: {e}")
        return []


def get_closed_trades():
    """
    Fetch recent closed trades from MT5
    """
    try:
        from .mt5_sync import get_mt5_closed_trades
        return get_mt5_closed_trades(days=7)
    except Exception as e:
        logger.warning(f"Failed to get closed trades: {e}")
        return []


def get_sts_signals():
    """
    Fetch recent STS (Simple Trading Solutions) signals from database
    Returns signals from the STS_SIGNALS source
    """
    try:
        from signals.models import MQL5Signal
        
        # Get only STS signals (Simple Trading Solutions signals)
        signals = MQL5Signal.objects.filter(
            source_name='STS_SIGNALS'
        ).order_by('-id')[:20].values(
            'id', 'symbol', 'direction', 'entry_price', 'stop_loss', 
            'take_profit', 'status', 'signal_strength', 'raw_signal_data'
        )
        
        # Convert to expected format
        formatted_signals = []
        for signal in signals:
            # Parse raw signal data if available
            raw_data = signal.get('raw_signal_data') or {}
            if isinstance(raw_data, str):
                try:
                    raw_data = json.loads(raw_data)
                except:
                    raw_data = {}
            elif raw_data is None:
                raw_data = {}
            
            formatted_signals.append({
                'id': signal['id'],
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry': float(signal['entry_price']),
                'sl': float(signal['stop_loss']),
                'tp': float(signal['take_profit']),
                'status': signal['status'],
                'profit': 0.0,  # TODO: Calculate actual profit from executed trades
                'timestamp': 'Just now',  # Placeholder
                'source': 'STS_SIGNALS'
            })
        
        return formatted_signals
            
    except Exception as e:
        logger.warning(f"Failed to get STS signals data: {e}")
        return []

def get_recent_signals():
    """
    Fetch recent signals from database
    Integrates with real database when available
    """
    try:
        # Try to get real signals from database
        from signals.models import MQL5Signal
        
        signals = MQL5Signal.objects.all().order_by('-id')[:10].values(
            'id', 'symbol', 'direction', 'entry_price', 'stop_loss', 
            'take_profit', 'status', 'timeframe_combination',
            'signal_strength', 'raw_signal_data'
        )
        
        # Convert to expected format
        formatted_signals = []
        for signal in signals:
            # Parse raw signal data if available
            raw_data = signal.get('raw_signal_data') or {}
            if isinstance(raw_data, str):
                try:
                    raw_data = json.loads(raw_data)
                except:
                    raw_data = {}
            elif raw_data is None:
                raw_data = {}
            
            # Get signals from database with source info
            from signals.models import MQL5Signal
            signal_obj = MQL5Signal.objects.get(id=signal['id'])
            
            formatted_signals.append({
                'id': signal['id'],
                'symbol': signal['symbol'],
                'direction': signal['direction'],  # Maps to BUY/SELL
                'strength': 0.75 if signal.get('signal_strength', '').lower() == 'medium' else 0.85,
                'entry': float(signal['entry_price']),
                'sl': float(signal['stop_loss']),
                'tp': float(signal['take_profit']),
                'status': signal['status'],
                'source': signal_obj.source_name,  # Add source information
                'timestamp': 'Just now',  # Placeholder since created field doesn't exist
                'timeframe': signal.get('timeframe_combination', 'H1/M15'),
                'rr_strategy': '1:2',
                'weekly_performance': 0,
                'llm_analysis': {
                    'reasoning': raw_data.get('reasoning', 'Analysis pending'),
                    'confidence': 0.75,
                    'break_even_price': None,
                    'halfway_tp': None
                }
            })
        
        if formatted_signals:
            return formatted_signals
            
    except Exception as e:
        logger.warning(f"Failed to get real signals data: {e}")
        print(f"DEBUG: Error getting signals: {e}")  # Debug print
    
    # Return empty list instead of mock data
    return []


def get_system_status():
    """
    Check system component status
    Will be replaced with real health checks in OSA 4
    """
    try:
        # TODO: Implement real health checks
        # - Django: always True if this function runs
        # - MT5: check MT5 connection
        # - MCP: check MCP server status
        # - LLM: check OpenAI API
        # - PURE EA: check EA status
        
        return {
            'django': True,
            'mt5': True,  # TODO: check_mt5_connection()
            'mcp': True,  # TODO: check_mcp_connection()
            'llm': True,  # TODO: check_llm_connection()
            'pure_ea': True,  # TODO: check_pure_ea_connection()
            'timeframe_sync': True
        }
    except Exception as e:
        return {
            'django': True,
            'mt5': False,
            'mcp': False,
            'llm': False,
            'pure_ea': False,
            'timeframe_sync': False,
            'error': str(e)
        }


def get_weekly_performance():
    """
    Calculate weekly performance for R:R strategy
    Will be replaced with real calculations in OSA 4
    """
    try:
        # TODO: Implement real weekly performance calculation
        # - Query trades from last 7 days
        # - Calculate P&L percentage per symbol
        # - Determine if upgrade to 1:2 R:R is warranted (≥10%)
        
        return {
            'EURUSD': {'pct': 12.3, 'trades': 4, 'upgraded': True},
            'GBPUSD': {'pct': 8.5, 'trades': 3, 'upgraded': False},
            'USDJPY': {'pct': 15.2, 'trades': 5, 'upgraded': True}
        }
    except Exception as e:
        return {}


def get_notifications():
    """
    Fetch recent notifications
    Will be replaced with real database query in OSA 4
    """
    try:
        # TODO: Implement real notifications system
        # from notifications.models import Notification
        # return Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        return [
            {
                'id': 1,
                'type': 'rr_upgrade',
                'title': 'R:R Strategy Upgraded - EURUSD',
                'message': '🎯 EURUSD R:R STRATEGY UPGRADED! Weekly profit 12.3% ≥ 10% → Now using 1:2 R:R with break-even logic',
                'timestamp': '2025-01-18 14:30:00',
                'read': False
            },
            {
                'id': 2,
                'type': 'timeframe_change',
                'title': 'Timeframe Updated - GBPUSD',
                'message': 'PURE EA timeframe changed to M15/M5 for enhanced scalping',
                'timestamp': '2025-01-18 13:15:00',
                'read': True
            }
        ]
    except Exception as e:
        return []


def get_process_flow():
    """
    Get current process flow status
    Static data for now, will be dynamic in OSA 4
    """
    return [
        {'id': 'pure_ea', 'name': 'PURE EA', 'status': 'active', 'icon': '🎯', 'desc': 'H1 BOS → M15 Retest'},
        {'id': 'django', 'name': 'Django', 'status': 'active', 'icon': '🌐', 'desc': 'Webhook Reception'},
        {'id': 'llm', 'name': 'LLM', 'status': 'processing', 'icon': '🤖', 'desc': 'GPT-4 Analysis'},
        {'id': 'mcp', 'name': 'MCP', 'status': 'pending', 'icon': '🧠', 'desc': 'Decision Engine'},
        {'id': 'mt5', 'name': 'MT5', 'status': 'pending', 'icon': '📈', 'desc': 'Trade Execution'}
    ]