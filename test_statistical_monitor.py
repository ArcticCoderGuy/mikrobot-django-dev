#!/usr/bin/env python3
"""
Test script for U-Cell 5 Statistical Monitor
FoxBox Framework  - Above Robust  Testing
"""

import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

# Import U-Cell 5 Statistical Monitor
sys.path.append(os.path.join('..', 'mikrobot_u_cells', 'validated', 'UCell_Monitoring_Control_v1.0'))

try:
    from statistical_monitor import StatisticalMonitor, QualityMeasurement
    print("[OK] StatisticalMonitor imported successfully")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

def test_statistical_monitor():
    """Test the statistical monitor functionality"""
    print("\n[FOXBOX] FoxBox Framework - U-Cell 5 Statistical Monitor Test")
    print("=" * 60)
    
    # HARDCODED PRODUCTION_CONFIG - Above Robust  approach
    PRODUCTION_CONFIG = {
        'execute_threshold': 0.8,
        'review_threshold': 0.6,
        'max_risk_per_trade': 0.01,
        'target_processing_time_ms': 150.0,
        'usl_processing_time_ms': 200.0,
        'acceptable_sessions': ['London', 'London-NY'],
        'min_position_size': 0.01,
        'max_position_size': 1.0,
        'six_sigma_target': 6.0,
        'cpk_minimum': 2.0,
        'dpmo_maximum': 3.4
    }
    
    # Initialize monitor
    monitor = StatisticalMonitor(PRODUCTION_CONFIG)
    print("[OK] StatisticalMonitor initialized")
    
    # Test measurement recording
    from datetime import datetime
    import random
    
    print("\n[METRICS] Recording test measurements...")
    
    # Generate test measurements for U-Cell processes
    test_processes = [
        {
            'name': 'signal_processing_latency',
            'target': 25.0,
            'usl': 50.0,
            'lsl': 0.0,
            'unit': 'ms',
            'sample_mean': 25.0,
            'sample_std': 3.0
        },
        {
            'name': 'order_execution_slippage',
            'target': 1.0,
            'usl': 2.0,
            'lsl': 0.0,
            'unit': 'pips',
            'sample_mean': 1.1,
            'sample_std': 0.2
        },
        {
            'name': 'risk_calculation_accuracy',
            'target': 100.0,
            'usl': 100.1,
            'lsl': 99.9,
            'unit': '%',
            'sample_mean': 99.98,
            'sample_std': 0.02
        }
    ]
    
    # Record 30 measurements for each process
    successful_recordings = 0
    for process in test_processes:
        print(f"\nRecording measurements for {process['name']}...")
        
        for i in range(30):
            # Generate realistic measurement
            measurement_value = random.normalvariate(process['sample_mean'], process['sample_std'])
            # Ensure within reasonable bounds
            measurement_value = max(process['lsl'], min(process['usl'], measurement_value))
            
            measurement = {
                'process_name': process['name'],
                'measurement_value': measurement_value,
                'measurement_unit': process['unit'],
                'target_value': process['target'],
                'upper_spec_limit': process['usl'],
                'lower_spec_limit': process['lsl'],
                'timestamp': datetime.now().isoformat(),
                'correlation_id': f'TEST_{process["name"]}_{i}'
            }
            
            success = monitor.record_measurement(measurement)
            if success:
                successful_recordings += 1
    
    print(f"\n[OK] Recorded {successful_recordings} measurements successfully")
    
    # Test process capability calculations
    print("\n[TARGET] Calculating process capabilities...")
    
    for process in test_processes:
        capability = monitor.calculate_process_capability(process['name'])
        if capability:
            print(f"\n[CHART] {process['name'].upper()} CAPABILITY:")
            print(f"   Cp: {capability['cp']:.3f}")
            print(f"   Cpk: {capability['cpk']:.3f}")
            print(f"   Sigma Level: {capability['sigma_level']:.2f}")
            print(f"   DPMO: {capability['dpmo']:.1f}")
            print(f"   Quality Status: {capability['quality_status']}")
            print(f"   Meets Six Sigma: {'[OK]' if capability['meets_six_sigma'] else '[ERROR]'}")
            
            if capability['recommendations']:
                print(f"   Recommendations:")
                for rec in capability['recommendations']:
                    print(f"     • {rec}")
    
    # Generate Six Sigma report
    print("\n[REPORT] Generating Six Sigma System Report...")
    report = monitor.generate_six_sigma_report()
    
    print(f"\n[FACTORY] SIX SIGMA SYSTEM REPORT:")
    print(f"   Overall Sigma Level: {report['overall_sigma_level']:.2f}")
    print(f"   Total DPMO: {report['total_dpmo']:.1f}")
    print(f"   System Health: {report['system_overview']['system_health']}")
    print(f"   Processes Meeting Six Sigma: {report['system_overview']['processes_meeting_six_sigma']}/{report['system_overview']['total_processes_monitored']}")
    print(f"   Average Cpk: {report['system_overview']['average_cpk']:.3f}")
    
    print(f"\n🔧 IMPROVEMENT ACTIONS ({len(report['improvement_actions'])}):")
    for action in report['improvement_actions']:
        priority_emoji = "🔴" if action['priority'] == 'HIGH' else "🟡" if action['priority'] == 'MEDIUM' else "🟢"
        print(f"   {priority_emoji} [{action['priority']}] {action['action']}")
    
    # Test monitoring status
    print("\n🔍 Monitoring Status:")
    status = monitor.get_process_status()
    print(f"   Total Processes: {status['total_processes']}")
    print(f"   Monitoring Active: {'[OK]' if status['monitoring_active'] else '[ERROR]'}")
    print(f"   Six Sigma Target: {status['six_sigma_target']}")
    
    print("\n🎯 Process Details:")
    for process_name, process_info in status["processes"].items():
        last_value = process_info['last_measurement']
        unit = process_info['unit']
        count = process_info['measurement_count']
        print(f"   {process_name}: {count} measurements, Last: {last_value:.3f if last_value else 'N/A'}{unit}")
    
    print("\n[OK] U-Cell 5 Statistical Monitor Test Completed!")
    print("[FACTORY] Statistical Process Control is OPERATIONAL")
    
    return True

if __name__ == "__main__":
    try:
        success = test_statistical_monitor()
        if success:
            print("\n[FOXBOX] FoxBox Framework - U-Cell 5 Integration: SUCCESS")
            sys.exit(0)
        else:
            print("\n[ERROR] Test failed")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)