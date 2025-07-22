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
from decimal import Decimal
import uuid
from django.utils import timezone

print("=== TESTISIGNAALIN LUONTI ===\n")

# Tarkista onko vanhoja signaaleja
existing_signals = MQL5Signal.objects.all()
print(f"Vanhoja signaaleja tietokannassa: {existing_signals.count()}")

# Luo uusi testisignaali
signal = MQL5Signal.objects.create(
    id=uuid.uuid4(),
    source_name="QA_TEST_MT5",
    symbol="EURUSD",
    direction="BUY",  # Ei action vaan direction
    entry_price=Decimal("1.1650"),
    stop_loss=Decimal("1.1600"),
    take_profit=Decimal("1.1700"),
    signal_strength="strong",  # Pitää olla 'weak', 'medium' tai 'strong'
    signal_timestamp=timezone.now(),  # Pakollinen kenttä, timezone-aware
    timeframe_combination="H1/M15",  # Oikea kenttänimi
    raw_signal_data={  # Lisätään raakadata
        "source": "QA Test",
        "test": True
    }
)

print(f"\n✅ Signaali luotu!")
print(f"ID: {signal.id}")
print(f"Symbol: {signal.symbol}")
print(f"Direction: {signal.direction}")
print(f"Entry: {signal.entry_price}")
print(f"SL: {signal.stop_loss} ({abs(signal.entry_price - signal.stop_loss) * 10000:.0f} pips)")
print(f"TP: {signal.take_profit} ({abs(signal.take_profit - signal.entry_price) * 10000:.0f} pips)")
print(f"Status: {signal.status}")
print(f"Received at: {signal.received_at}")

# Tarkista että signaali tallentui
saved_signal = MQL5Signal.objects.get(id=signal.id)
print(f"\n✅ Signaali löytyy tietokannasta!")
print(f"Signaaleja yhteensä: {MQL5Signal.objects.count()}")