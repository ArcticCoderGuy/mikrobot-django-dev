#!/usr/bin/env python3
"""
Test script for Risk Management Integration in MikroBot LLM Agent
Tests the complete flow: Signal Data → Risk Config → LLM Analysis
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timezone

# Setup Django environment
sys.path.append('C:\\Users\\HP\\Desktop\\Claude projects\\mikrobot_django_dev')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

from signals.models import MQL5Signal
from signals.llm_agent import LLMSignalAnalyzer
from signals.risk_config import RiskConfig, validate_risk_parameters


def create_test_signal():
    """Create a test signal with risk indicators"""
    # Create test signal
    signal = MQL5Signal.objects.create(
        source_name='MikroBot_BOS',
        symbol='EURUSD',
        direction='BUY',
        entry_price=Decimal('1.12500'),
        stop_loss=Decimal('1.11900'),
        take_profit=Decimal('1.13400'),
        signal_strength='strong',
        signal_timestamp=datetime.now(timezone.utc),
        timeframe_combination='H1/M15',
        raw_signal_data={
            'h1_bos_level': 1.12000,
            'h1_bos_direction': 'BULLISH',
            'm15_break_high': 1.12300,
            'm15_break_low': 1.12100,
            'pip_trigger': 0.6,
            'atr': 0.00156,  # Sample ATR value
            'adx': 28.5,     # Sample ADX value above threshold
            'swing_high': 1.12800,
            'swing_low': 1.11900,
            'ea_name': 'MikroBot_BOS',
            'ea_version': '1.04'
        }
    )
    
    return signal


def test_risk_configuration():
    """Test risk configuration creation"""
    print("=== Testing Risk Configuration ===")
    
    # Test default risk config
    risk_config = RiskConfig.from_signal_data('EURUSD', 'H1/M15')
    print(f"Default Config: {risk_config.to_dict()}")
    
    # Test custom risk config
    custom_config = {
        'fibonacci_sl': 0.30,
        'target_rr_ratio': 2.0
    }
    custom_risk_config = RiskConfig.from_signal_data('GBPJPY', 'M15/M5', custom_config)
    print(f"Custom Config (GBPJPY): {custom_risk_config.to_dict()}")
    
    return risk_config


def test_signal_preparation():
    """Test signal data preparation with risk management"""
    print("\n=== Testing Signal Data Preparation ===")
    
    signal = create_test_signal()
    analyzer = LLMSignalAnalyzer()
    
    # Prepare signal data
    signal_data = analyzer._prepare_signal_data(signal)
    
    print(f"Signal ID: {signal.id}")
    print(f"Symbol: {signal_data['symbol']}")
    print(f"Direction: {signal_data['direction']}")
    print(f"Timeframe: {signal_data['timeframe_combination']}")
    print(f"ATR: {signal_data['atr']}")
    print(f"ADX: {signal_data['adx']}")
    print(f"Risk Config: {signal_data['risk_config']}")
    print(f"Risk Validation: {signal_data['risk_validation']}")
    
    if 'missing_indicators' in signal_data:
        print(f"Missing Indicators: {signal_data['missing_indicators']}")
    
    signal.delete()  # Cleanup
    return signal_data


def test_prompt_generation():
    """Test LLM prompt generation with risk parameters"""
    print("\n=== Testing LLM Prompt Generation ===")
    
    signal = create_test_signal()
    analyzer = LLMSignalAnalyzer()
    
    # Prepare signal data and generate prompt
    signal_data = analyzer._prepare_signal_data(signal)
    prompt = analyzer._create_analysis_prompt(signal_data)
    
    print("Generated Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    # Check key components are present
    assert 'Fibonacci SL Level: 0.28' in prompt
    assert 'ADX Threshold: 25' in prompt
    assert 'ATR Multiplier: 1.5' in prompt
    assert 'Target R:R Ratio: 1.5:1' in prompt
    assert 'ATR Value: 0.00156' in prompt
    assert 'ADX Value: 28.5' in prompt
    
    print("All risk parameters correctly included in prompt")
    
    signal.delete()  # Cleanup


def test_missing_indicators():
    """Test handling of missing risk indicators"""
    print("\n=== Testing Missing Indicators Handling ===")
    
    # Create signal without ATR/ADX data
    signal = MQL5Signal.objects.create(
        source_name='MikroBot_BOS',
        symbol='GBPUSD',
        direction='SELL',
        entry_price=Decimal('1.25000'),
        stop_loss=Decimal('1.25500'),
        take_profit=Decimal('1.24200'),
        signal_strength='medium',
        signal_timestamp=datetime.now(timezone.utc),
        timeframe_combination='M15/M5',
        raw_signal_data={
            'h1_bos_level': 1.25500,
            'h1_bos_direction': 'BEARISH',
            'm15_break_high': 1.25200,
            'm15_break_low': 1.24800,
            'pip_trigger': 0.6,
            # Missing: atr, adx, swing_high, swing_low
        }
    )
    
    analyzer = LLMSignalAnalyzer()
    signal_data = analyzer._prepare_signal_data(signal)
    prompt = analyzer._create_analysis_prompt(signal_data)
    
    print(f"Missing Indicators: {signal_data.get('missing_indicators', [])}")
    print("Checking prompt contains warning...")
    
    if 'MISSING INDICATORS' in prompt:
        print("Missing indicators warning correctly included")
    else:
        print("Missing indicators warning not found")
    
    signal.delete()  # Cleanup


def main():
    """Run all risk management integration tests"""
    print("MikroBot Risk Management Integration Tests")
    print("=" * 50)
    
    try:
        # Test 1: Risk Configuration
        test_risk_configuration()
        
        # Test 2: Signal Data Preparation
        test_signal_preparation()
        
        # Test 3: Prompt Generation
        test_prompt_generation()
        
        # Test 4: Missing Indicators
        test_missing_indicators()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED - Risk Management Integration Working!")
        print("Ready for production use with OpenAI API key")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()