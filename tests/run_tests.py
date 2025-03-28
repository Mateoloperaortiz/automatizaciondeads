#!/usr/bin/env python
import os
import sys
import pytest
import argparse

def run_tests(test_type=None, verbose=False):
    """
    Run the tests based on the specified type.
    
    Args:
        test_type (str): Type of test to run (unit, integration, e2e, security, all)
        verbose (bool): Whether to run tests in verbose mode
    """
    # Base pytest arguments
    pytest_args = ['-v'] if verbose else []
    
    # Add test file paths based on test type
    if test_type == 'unit':
        print("Running unit tests...")
        pytest_args.append('tests/test_api_endpoints.py')
    elif test_type == 'integration':
        print("Running integration tests...")
        pytest_args.append('tests/test_integration.py')
    elif test_type == 'e2e':
        print("Running end-to-end tests...")
        pytest_args.append('tests/test_end_to_end.py')
    elif test_type == 'security':
        print("Running security tests...")
        pytest_args.append('tests/test_security.py')
    elif test_type == 'all' or test_type is None:
        print("Running all tests...")
        pytest_args.append('tests/')
    else:
        print(f"Unknown test type: {test_type}")
        return 1
    
    # Run the tests
    return pytest.main(pytest_args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tests for Ad Automation P-01')
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'security', 'all'],
                        default='all', help='Type of tests to run')
    parser.add_argument('--verbose', action='store_true', help='Run tests in verbose mode')
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Run the tests
    exit_code = run_tests(args.type, args.verbose)
    
    # Exit with the pytest exit code
    sys.exit(exit_code) 