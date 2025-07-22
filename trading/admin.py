from django.contrib import admin
from django.utils.html import format_html
from .models import Trade, TradingSession

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """
    Admin interface for Trade management
    """
    
    list_display = [
        'trade_summary',
        'status_badge',
        'direction',
        'pnl_display',
        'execution_time',
        'duration_display'
    ]
    
    list_filter = [
        'status',
        'direction',
        'symbol',
        'exit_reason',
        'execution_time'
    ]
    
    search_fields = [
        'symbol',
        'mt5_ticket',
        'mql5_signal__source_name'
    ]
    
    readonly_fields = [
        'id',
        'django_decision_time',
        'net_profit_loss',
        'duration_minutes',
        'execution_delay_seconds',
        'pips_display'
    ]
    
    fieldsets = (
        ('Trade Information', {
            'fields': ('id', 'mt5_ticket', 'mt5_order_type')
        }),
        ('Signal Link', {
            'fields': ('mql5_signal',)
        }),
        ('Trading Details', {
            'fields': (
                'symbol',
                'direction',
                'entry_price',
                'exit_price',
                'stop_loss',
                'take_profit',
                'volume'
            )
        }),
        ('Financial Results', {
            'fields': (
                'gross_profit_loss',
                'commission',
                'swap',
                'net_profit_loss',
                'pips_display'
            )
        }),
        ('Status & Exit', {
            'fields': (
                'status',
                'exit_reason'
            )
        }),
        ('Timing', {
            'fields': (
                'signal_time',
                'execution_time',
                'close_time',
                'duration_minutes',
                'execution_delay_seconds'
            )
        }),
        ('Performance', {
            'fields': (
                'max_drawdown',
                'max_profit'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )
    
    # Custom display methods
    def trade_summary(self, obj):
        return f"#{obj.mt5_ticket}: {obj.symbol}"
    trade_summary.short_description = "Trade"
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'opened': '#17a2b8',
            'closed_profit': '#28a745',
            'closed_loss': '#dc3545',
            'closed_breakeven': '#6c757d',
            'cancelled': '#6c757d',
            'error': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def pnl_display(self, obj):
        if obj.net_profit_loss is not None:
            color = '#28a745' if obj.net_profit_loss > 0 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">${}</span>',
                color,
                obj.net_profit_loss
            )
        return '-'
    pnl_display.short_description = "P&L"
    
    def duration_display(self, obj):
        if obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            return f"{hours}h {minutes}m"
        return '-'
    duration_display.short_description = "Duration"
    
    def pips_display(self, obj):
        pips = obj.calculate_pips()
        if pips is not None:
            color = '#28a745' if pips > 0 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} pips</span>',
                color,
                pips
            )
        return '-'
    pips_display.short_description = "Pips"

@admin.register(TradingSession)
class TradingSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for Trading Sessions
    """
    
    list_display = [
        'session_name',
        'start_time',
        'total_trades',
        'win_rate_display',
        'total_pnl_display'
    ]
    
    list_filter = [
        'session_name',
        'start_time'
    ]
    
    search_fields = [
        'session_name'
    ]
    
    filter_horizontal = ['trades']
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'session_name',
                'start_time',
                'end_time'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'total_trades',
                'winning_trades',
                'losing_trades',
                'total_pnl'
            )
        }),
        ('Risk Metrics', {
            'fields': (
                'max_concurrent_trades',
                'max_drawdown_session'
            )
        }),
        ('Trades', {
            'fields': ('trades',)
        })
    )
    
    def win_rate_display(self, obj):
        win_rate = obj.win_rate()
        color = '#28a745' if win_rate >= 60 else '#ffc107' if win_rate >= 40 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            win_rate
        )
    win_rate_display.short_description = "Win Rate"
    
    def total_pnl_display(self, obj):
        color = '#28a745' if obj.total_pnl > 0 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${}</span>',
            color,
            obj.total_pnl
        )
    total_pnl_display.short_description = "Total P&L"
