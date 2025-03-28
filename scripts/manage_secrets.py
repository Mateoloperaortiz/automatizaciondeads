#!/usr/bin/env python3
"""
Command-line utility for managing secrets in Google Cloud Secret Manager.

This script provides functionality to import/export secrets between 
.env files and Google Cloud Secret Manager.
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import app modules
from app.utils.gcp_secret_manager import secret_manager, is_secret_manager_available

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('secret-manager')

def load_env_file(file_path):
    """Load environment variables from a .env file."""
    env_vars = {}
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        return env_vars
    except Exception as e:
        logger.error(f"Error loading .env file: {str(e)}")
        return None

def save_env_file(file_path, env_vars):
    """Save environment variables to a .env file."""
    try:
        with open(file_path, 'w') as f:
            f.write("# Generated by MagnetoCursor Secret Manager Utility\n")
            f.write("# This file contains secrets exported from Google Cloud Secret Manager\n\n")
            
            for key, value in sorted(env_vars.items()):
                f.write(f"{key}={value}\n")
        
        return True
    except Exception as e:
        logger.error(f"Error saving .env file: {str(e)}")
        return False

def import_secrets(args):
    """Import secrets from .env file to Secret Manager."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # Load environment variables from .env file
    env_vars = load_env_file(args.file)
    if not env_vars:
        return False
    
    # Filter variables based on prefix
    if args.prefix:
        filtered_vars = {k: v for k, v in env_vars.items() if k.startswith(args.prefix)}
        logger.info(f"Filtered {len(filtered_vars)} variables with prefix {args.prefix}")
    else:
        filtered_vars = env_vars
    
    # Import to Secret Manager
    success = secret_manager.import_secrets_from_env(filtered_vars)
    
    if success:
        logger.info(f"Successfully imported {len(filtered_vars)} secrets to Secret Manager")
    else:
        logger.error("Failed to import some or all secrets to Secret Manager")
    
    return success

def export_secrets(args):
    """Export secrets from Secret Manager to .env file."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # Export from Secret Manager
    env_vars = secret_manager.export_all_secrets_to_env()
    
    # Filter variables based on prefix
    if args.prefix:
        filtered_vars = {k: v for k, v in env_vars.items() if k.startswith(args.prefix)}
        logger.info(f"Filtered {len(filtered_vars)} variables with prefix {args.prefix}")
    else:
        filtered_vars = env_vars
    
    # Save to .env file
    success = save_env_file(args.file, filtered_vars)
    
    if success:
        logger.info(f"Successfully exported {len(filtered_vars)} secrets to {args.file}")
    else:
        logger.error(f"Failed to export secrets to {args.file}")
    
    return success

def list_secrets(args):
    """List all secrets in Secret Manager."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # List secrets
    secrets = secret_manager.list_secrets()
    
    # Filter secrets based on prefix
    if args.prefix:
        filtered_secrets = [s for s in secrets if s['name'].startswith(args.prefix)]
        logger.info(f"Filtered {len(filtered_secrets)} secrets with prefix {args.prefix}")
    else:
        filtered_secrets = secrets
    
    # Print secrets
    print(f"\nFound {len(filtered_secrets)} secrets in Secret Manager:")
    for secret in sorted(filtered_secrets, key=lambda s: s['name']):
        print(f"  - {secret['name']} (created: {secret['create_time']})")
    
    return True

def get_secret_value(args):
    """Get a secret value from Secret Manager."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # Get secret value
    value = secret_manager.get_secret(args.name)
    
    if value is not None:
        if args.mask:
            # Mask the secret value
            if len(value) <= 8:
                masked = '*' * len(value)
            else:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
            print(f"{args.name}: {masked}")
        else:
            print(f"{args.name}: {value}")
        return True
    else:
        logger.error(f"Secret {args.name} not found or access denied")
        return False

def set_secret_value(args):
    """Set a secret value in Secret Manager."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # Set secret value
    success = secret_manager.create_or_update_secret(args.name, args.value)
    
    if success:
        logger.info(f"Successfully set value for secret {args.name}")
    else:
        logger.error(f"Failed to set value for secret {args.name}")
    
    return success

def delete_secret(args):
    """Delete a secret from Secret Manager."""
    if not is_secret_manager_available():
        logger.error("Google Cloud Secret Manager is not available")
        return False
    
    # Delete secret
    success = secret_manager.delete_secret(args.name)
    
    if success:
        logger.info(f"Successfully deleted secret {args.name}")
    else:
        logger.error(f"Failed to delete secret {args.name}")
    
    return success

def main():
    """Main entry point for the script."""
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='MagnetoCursor Secret Manager Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Import secrets from .env file:
    python manage_secrets.py import .env
  
  Export secrets to .env file:
    python manage_secrets.py export .env
  
  List all secrets:
    python manage_secrets.py list
  
  Get a secret value:
    python manage_secrets.py get META_APP_ID
  
  Set a secret value:
    python manage_secrets.py set META_APP_ID 123456789
  
  Delete a secret:
    python manage_secrets.py delete META_APP_ID
        """
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import secrets from .env file')
    import_parser.add_argument('file', help='Path to .env file')
    import_parser.add_argument('--prefix', help='Only import variables with this prefix')
    import_parser.set_defaults(func=import_secrets)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export secrets to .env file')
    export_parser.add_argument('file', help='Path to output .env file')
    export_parser.add_argument('--prefix', help='Only export variables with this prefix')
    export_parser.set_defaults(func=export_secrets)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all secrets')
    list_parser.add_argument('--prefix', help='Only list secrets with this prefix')
    list_parser.set_defaults(func=list_secrets)
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a secret value')
    get_parser.add_argument('name', help='Secret name')
    get_parser.add_argument('--mask', action='store_true', help='Mask the secret value')
    get_parser.set_defaults(func=get_secret_value)
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a secret value')
    set_parser.add_argument('name', help='Secret name')
    set_parser.add_argument('value', help='Secret value')
    set_parser.set_defaults(func=set_secret_value)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a secret')
    delete_parser.add_argument('name', help='Secret name')
    delete_parser.set_defaults(func=delete_secret)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()