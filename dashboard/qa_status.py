"""
QA Status Reader
Lukee automaattisten QA-testien tulokset
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from django.conf import settings

def get_latest_qa_results() -> Optional[Dict[str, Any]]:
    """Hae viimeisimmät QA-testitulokset"""
    try:
        results_file = os.path.join(settings.BASE_DIR, 'qa_results.json')
        
        if not os.path.exists(results_file):
            return None
            
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
        # Lisää viime ajon ajankohta
        timestamp = datetime.fromisoformat(results['timestamp'])
        results['last_run'] = timestamp
        results['time_since_last'] = datetime.now() - timestamp
        results['time_since_last_minutes'] = int(results['time_since_last'].total_seconds() / 60)
        results['is_recent'] = results['time_since_last'] < timedelta(minutes=20)
        
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'last_run': None,
            'overall_status': 'ERROR'
        }

def get_qa_status_summary() -> Dict[str, Any]:
    """Hae QA-tilan lyhyt yhteenveto"""
    results = get_latest_qa_results()
    
    if not results:
        return {
            'status': 'NO_DATA',
            'message': 'QA automation not run yet',
            'last_run': None,
            'pass_rate': 0,
            'next_run_in': '15 minutes (estimated)'
        }
    
    if 'error' in results:
        return {
            'status': 'ERROR',
            'message': f"QA error: {results['error']}",
            'last_run': None,
            'pass_rate': 0
        }
    
    # Manual testing - ei automaattista ajastusta
    next_run_text = "Manual (Click Run Tests Now)"
    
    summary = results.get('summary', {})
    
    return {
        'status': results.get('overall_status', 'UNKNOWN'),
        'message': f"{summary.get('passed', 0)}/{summary.get('total_tests', 0)} tests passed",
        'last_run': results.get('last_run'),
        'pass_rate': summary.get('pass_rate', 0),
        'next_run_in': next_run_text,
        'is_recent': results.get('is_recent', False),
        'detailed_results': results.get('tests', {}),
        'time_since_last': results.get('time_since_last')
    }