import os
import sys
import django

# Fix Unicode on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import json

print("=== DJANGO SESSION DEBUG ===\n")

# Hae kaikki aktiiviset sessiot
sessions = Session.objects.all()
print(f"Aktiivisia sessioita: {sessions.count()}")

for session in sessions:
    try:
        decoded_data = session.get_decoded()
        print(f"\nSession ID: {session.session_key[:10]}...")
        print(f"Expires: {session.expire_date}")
        
        # Etsi trading session asetukset
        trading_settings = {}
        for key in ['trade_london', 'trade_new_york', 'trade_tokyo', 'currency_pair', 'risk_percentage']:
            if key in decoded_data:
                trading_settings[key] = decoded_data[key]
        
        if trading_settings:
            print("Trading asetukset:")
            for key, value in trading_settings.items():
                print(f"  {key}: {value}")
        else:
            print("Ei trading asetuksia löytynyt")
            
    except Exception as e:
        print(f"Error decoding session: {e}")

print("\n=== END DEBUG ===")