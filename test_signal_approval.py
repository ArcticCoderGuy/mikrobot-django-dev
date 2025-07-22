import os
import sys
import django

# Fix Unicode on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

from signals.models import MQL5Signal
from django.utils import timezone

print("=== SIGNAALIN HYVÄKSYNTÄ ===\n")

# Hae viimeisin pending signaali
pending_signals = MQL5Signal.objects.filter(status='pending').order_by('-received_at')
print(f"Pending signaaleja: {pending_signals.count()}")

if pending_signals.exists():
    signal = pending_signals.first()
    print(f"\nKäsitellään signaalia:")
    print(f"ID: {signal.id}")
    print(f"Symbol: {signal.symbol}")
    print(f"Direction: {signal.direction}")
    print(f"Entry: {signal.entry_price}")
    print(f"Status: {signal.status}")
    
    # Tarkista R:R ratio
    rr_ratio = signal.calculate_risk_reward_ratio()
    print(f"\nR:R Ratio: {rr_ratio}")
    print(f"Valid signal: {signal.is_valid_signal()}")
    
    # Hyväksy signaali
    signal.status = 'approved'
    signal.save()
    
    print(f"\n✅ Signaali hyväksytty!")
    print(f"Uusi status: {signal.status}")
    
    # Tarkista kaikki approved signaalit
    approved_count = MQL5Signal.objects.filter(status='approved').count()
    print(f"\nHyväksyttyjä signaaleja yhteensä: {approved_count}")
    
else:
    print("❌ Ei pending signaaleja käsiteltäväksi!")