from django.db import models
from django.utils import timezone
from signals.models import MQL5Signal
import uuid

class Trade(models.Model):
    """
    Tallentaa kaikki toteutuneet kaupat
    Yhdistää MQL5 signaalin lopulliseen tulokseen
    """
    
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to original signal
    mql5_signal = models.OneToOneField(
        MQL5Signal, 
        on_delete=models.CASCADE,
        related_name='trade',
        help_text="Original signal that created this trade"
    )
    
    # MetaTrader information
    mt5_ticket = models.BigIntegerField(
        unique=True,
        help_text="MetaTrader 5 ticket number"
    )
    mt5_order_type = models.CharField(
        max_length=20,
        help_text="ORDER_TYPE_BUY, ORDER_TYPE_SELL, etc."
    )
    
    # Trade execution details
    symbol = models.CharField(max_length=20)
    direction = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    
    # Actual execution prices (may differ from signal)
    entry_price = models.DecimalField(
        max_digits=10, 
        decimal_places=5,
        help_text="Actual entry price executed"
    )
    exit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=5, 
        null=True, 
        blank=True,
        help_text="Actual exit price (when closed)"
    )
    
    # Risk management executed
    stop_loss = models.DecimalField(max_digits=10, decimal_places=5)
    take_profit = models.DecimalField(max_digits=10, decimal_places=5)
    
    # Position sizing
    volume = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Actual lot size traded"
    )
    
    # Trade status
    STATUS_CHOICES = [
        ('pending', 'Pending Execution'),
        ('opened', 'Position Open'),
        ('closed_profit', 'Closed with Profit'),
        ('closed_loss', 'Closed with Loss'),
        ('closed_breakeven', 'Closed at Breakeven'),
        ('cancelled', 'Cancelled'),
        ('error', 'Execution Error'),
    ]
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Financial results
    gross_profit_loss = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Gross P&L in account currency"
    )
    commission = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        help_text="Broker commission"
    )
    swap = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        help_text="Overnight swap charges"
    )
    net_profit_loss = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Net P&L after commission and swap"
    )
    
    # Timing
    signal_time = models.DateTimeField(help_text="When signal was created")
    execution_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When trade was opened in MT5"
    )
    close_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When trade was closed in MT5"
    )
    
    # Performance metrics
    duration_minutes = models.IntegerField(
        null=True, 
        blank=True,
        help_text="How long trade was open (minutes)"
    )
    max_drawdown = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum unrealized loss during trade"
    )
    max_profit = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum unrealized profit during trade"
    )
    
    # Exit reason
    EXIT_REASON_CHOICES = [
        ('take_profit', 'Take Profit Hit'),
        ('stop_loss', 'Stop Loss Hit'),
        ('manual', 'Manual Close'),
        ('trailing_stop', 'Trailing Stop'),
        ('time_exit', 'Time-based Exit'),
        ('risk_management', 'Risk Management Override'),
        ('market_close', 'Market Close'),
    ]
    
    exit_reason = models.CharField(
        max_length=20, 
        choices=EXIT_REASON_CHOICES, 
        null=True, 
        blank=True
    )
    
    # Django analysis
    django_decision_time = models.DateTimeField(
        auto_now_add=True,
        help_text="When Django made the trade decision"
    )
    execution_delay_seconds = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Delay between signal and execution"
    )
    
    # Notes and comments
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this trade"
    )
    
    class Meta:
        ordering = ['-execution_time']
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        
    def __str__(self):
        return f"Trade #{self.mt5_ticket}: {self.direction} {self.symbol} @ {self.entry_price}"
    
    def calculate_pips(self):
        """Calculate pips gained/lost"""
        if not self.exit_price:
            return None
            
        pip_value = 0.0001 if 'JPY' not in self.symbol else 0.01
        
        if self.direction == 'BUY':
            pips = (float(self.exit_price) - float(self.entry_price)) / pip_value
        else:  # SELL
            pips = (float(self.entry_price) - float(self.exit_price)) / pip_value
            
        return round(pips, 1)
    
    def is_profitable(self):
        """Check if trade was profitable"""
        if self.net_profit_loss is None:
            return None
        return self.net_profit_loss > 0
    
    def calculate_ror(self):
        """Calculate Risk of Ruin ratio"""
        signal_risk_reward = self.mql5_signal.calculate_risk_reward_ratio()
        if signal_risk_reward and self.net_profit_loss:
            actual_result = float(self.net_profit_loss)
            return round(actual_result / signal_risk_reward, 2)
        return None
    
    def save(self, *args, **kwargs):
        """Override save to calculate derived fields"""
        # Calculate net P&L
        if self.gross_profit_loss is not None:
            self.net_profit_loss = self.gross_profit_loss - self.commission - self.swap
        
        # Calculate duration
        if self.execution_time and self.close_time:
            duration = self.close_time - self.execution_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        
        # Calculate execution delay
        if self.signal_time and self.execution_time:
            delay = self.execution_time - self.signal_time
            self.execution_delay_seconds = int(delay.total_seconds())
            
        super().save(*args, **kwargs)


class TradingSession(models.Model):
    """
    Group trades by trading session for analysis
    """
    
    session_name = models.CharField(max_length=100, help_text="e.g. 'London Open', 'NY Session'")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Session performance
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    total_pnl = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Risk metrics
    max_concurrent_trades = models.IntegerField(default=0)
    max_drawdown_session = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    
    trades = models.ManyToManyField(Trade, blank=True, related_name='trading_sessions')
    
    class Meta:
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.session_name} ({self.start_time.date()})"
    
    def win_rate(self):
        """Calculate win rate percentage"""
        if self.total_trades > 0:
            return round((self.winning_trades / self.total_trades) * 100, 1)
        return 0.0
