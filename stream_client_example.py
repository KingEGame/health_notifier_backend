#!/usr/bin/env python3
"""
Пример клиента для работы со streaming API пациентов
Example client for working with patient streaming API
"""

import requests
import json
import sys
from typing import Iterator, Dict, Any

def stream_patients(
    base_url: str = "http://localhost:5000",
    risk_level: str = None,
    location: str = None,
    batch_size: int = 10,
    include_ai_suggestions: bool = True,
    include_notifications: bool = True
) -> Iterator[Dict[str, Any]]:
    """
    Stream patients from the API
    
    Args:
        base_url: Base URL of the API
        risk_level: Filter by risk level ('low', 'medium', 'high')
        location: Filter by zip code
        batch_size: Number of patients per batch
        include_ai_suggestions: Include AI suggestions
        include_notifications: Include notifications
    
    Yields:
        Dictionary containing patient data or metadata
    """
    
    # Build URL with parameters
    url = f"{base_url}/api/patients/with-risks/stream"
    params = {
        'batch_size': batch_size,
        'include_ai_suggestions': str(include_ai_suggestions).lower(),
        'include_notifications': str(include_notifications).lower()
    }
    
    if risk_level:
        params['risk_level'] = risk_level
    if location:
        params['location'] = location
    
    try:
        # Make streaming request
        response = requests.get(url, params=params, stream=True)
        response.raise_for_status()
        
        # Process each line
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    yield data
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}", file=sys.stderr)
                    continue
                    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}", file=sys.stderr)
        raise

def process_patients_stream(
    base_url: str = "http://localhost:5000",
    risk_level: str = None,
    location: str = None,
    batch_size: int = 10
):
    """
    Process patients from streaming API and print results
    """
    
    print(f"Starting patient stream from {base_url}")
    print(f"Filters: risk_level={risk_level}, location={location}")
    print(f"Batch size: {batch_size}")
    print("-" * 50)
    
    total_patients = 0
    risk_counts = {'low': 0, 'medium': 0, 'high': 0}
    
    try:
        for data in stream_patients(base_url, risk_level, location, batch_size):
            if data['type'] == 'metadata':
                print(f"📊 Total patients to process: {data['total_patients']}")
                print(f"📦 Batch size: {data['batch_size']}")
                print(f"🔍 Filters: {data['filters_applied']}")
                print()
                
            elif data['type'] == 'batch':
                patients = data['patients']
                processed = data['processed_count']
                total = data['total_patients']
                
                print(f"📋 Batch received: {len(patients)} patients")
                print(f"📈 Progress: {processed}/{total} ({processed/total*100:.1f}%)")
                
                # Count risks in this batch
                for patient in patients:
                    risk_counts[patient['risk_level']] += 1
                    total_patients += 1
                    
                    # Print high-risk patients
                    if patient['risk_level'] == 'high':
                        print(f"  🚨 HIGH RISK: {patient['name']} (ID: {patient['patient_id']}, Score: {patient['risk_score']})")
                
                print()
                
            elif data['type'] == 'summary':
                print("=" * 50)
                print("📊 FINAL SUMMARY")
                print("=" * 50)
                print(f"Total processed: {data['total_processed']}")
                print(f"Total available: {data['total_available_patients']}")
                print(f"Patients at risk: {data['patients_at_risk']}")
                print(f"Risk distribution: {data['risk_distribution']}")
                print()
                
            elif data['type'] == 'error':
                print(f"❌ Error: {data['error']}")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️  Stream interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream patients from health notifier API')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--risk-level', choices=['low', 'medium', 'high'], help='Filter by risk level')
    parser.add_argument('--location', help='Filter by zip code')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for streaming')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI suggestions for faster processing')
    parser.add_argument('--no-notifications', action='store_true', help='Disable notifications for faster processing')
    
    args = parser.parse_args()
    
    process_patients_stream(
        base_url=args.url,
        risk_level=args.risk_level,
        location=args.location,
        batch_size=args.batch_size
    )

if __name__ == '__main__':
    main()
