#!/usr/bin/env python3
"""
Test runner for weather API and environment configuration tests
"""

import sys
import os
import pytest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_weather_tests():
    """Run all weather-related tests"""
    print("🌤️  Running Weather API and Environment Configuration Tests")
    print("=" * 60)
    
    # Test files to run
    test_files = [
        'tests/test_weather_api.py',
        'tests/test_env_config.py',
        'tests/test_api_integration.py'
    ]
    
    # Run tests with verbose output
    args = [
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--color=yes',  # Colored output
        '--durations=10',  # Show 10 slowest tests
    ] + test_files
    
    # Run the tests
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ {exit_code} test(s) failed!")
    
    return exit_code

def run_specific_test_category(category):
    """Run specific test category"""
    test_files = {
        'weather': ['tests/test_weather_api.py'],
        'env': ['tests/test_env_config.py'],
        'integration': ['tests/test_api_integration.py'],
        'all': ['tests/test_weather_api.py', 'tests/test_env_config.py', 'tests/test_api_integration.py']
    }
    
    if category not in test_files:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_files.keys())}")
        return 1
    
    print(f"🧪 Running {category} tests...")
    print("=" * 40)
    
    args = [
        '-v',
        '--tb=short',
        '--color=yes',
        '--durations=10',
    ] + test_files[category]
    
    exit_code = pytest.main(args)
    return exit_code

def main():
    """Main function"""
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        return run_specific_test_category(category)
    else:
        return run_weather_tests()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
