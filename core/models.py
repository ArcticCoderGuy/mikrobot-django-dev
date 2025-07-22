from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    """Store user-specific trading settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    currency_pair = models.CharField(max_length=10, default='EURUSD')
    risk_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    stop_loss_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.28, 
                                        help_text='Fibonacci stop loss level (0.15, 0.28, 0.50, 0.63)')
    weekly_profit_threshold = models.DecimalField(max_digits=4, decimal_places=1, default=10.0,
                                                help_text='Weekly profit % threshold for 1:2 R:R upgrade')
    break_even_buffer_pips = models.DecimalField(max_digits=4, decimal_places=1, default=2.0,
                                               help_text='Buffer pips for break-even activation at 1:1')
    # Trading Sessions
    trade_london = models.BooleanField(default=True, help_text='Trade during London session (10:00-19:00 EET)')
    trade_new_york = models.BooleanField(default=True, help_text='Trade during New York session (15:30-00:30 EET)')
    trade_tokyo = models.BooleanField(default=False, help_text='Trade during Tokyo session (03:00-12:00 EET)')
    
    # Notifications
    notification_email = models.EmailField(blank=True, null=True, help_text='Email for trading notifications')
    notification_email_enabled = models.BooleanField(default=True, help_text='Enable email notifications')
    metaquotes_id = models.CharField(max_length=20, blank=True, null=True, help_text='MetaTrader ID for push notifications')
    metaquotes_enabled = models.BooleanField(default=False, help_text='Enable MetaQuotes push notifications')
    telegram_username = models.CharField(max_length=50, blank=True, null=True, help_text='Telegram username (without @)')
    telegram_enabled = models.BooleanField(default=False, help_text='Enable Telegram notifications')
    sms_phone = models.CharField(max_length=20, blank=True, null=True, help_text='Phone number for SMS notifications')
    sms_enabled = models.BooleanField(default=False, help_text='Enable SMS notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
    
    def __str__(self):
        return f"{self.user.username} - {self.currency_pair} ({self.risk_percentage}%)"
