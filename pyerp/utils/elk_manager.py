import json
import os
import socket
from pathlib import Path

def get_external_connections_config():
    """
    Load the external_connections.json configuration file.
    """
    config_path = Path(__file__).parents[1] / "config" / "external_connections.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading external connections config: {e}")
        return {}

def is_remote_elk_enabled():
    """
    Check if remote ELK is enabled in the configuration.
    """
    config = get_external_connections_config()
    
    if not config:
        return False
    
    # Check if remote_elk is in the config and if it's enabled
    if isinstance(config.get('remote_elk'), dict):
        return config['remote_elk'].get('enabled', False)
    
    return False

def get_hostname():
    """
    Get the current machine's hostname for developer identification.
    """
    return socket.gethostname()

def configure_elk_logging():
    """
    Configure ELK logging based on environment and settings.
    
    Returns a dictionary with logging configuration that can be used
    in Django settings or other logging configuration.
    """
    # Get current environment
    environment = os.environ.get('PYERP_ENV', 'development')
    
    # Default ELK settings
    elk_config = {
        'enabled': False,
        'host': os.environ.get('ELASTICSEARCH_HOST', 'localhost'),
        'port': os.environ.get('ELASTICSEARCH_PORT', '9200'),
        'username': os.environ.get('ELASTICSEARCH_USERNAME', ''),
        'password': os.environ.get('ELASTICSEARCH_PASSWORD', ''),
        'index_prefix': os.environ.get('ELASTICSEARCH_INDEX_PREFIX', 'pyerp'),
        'developer_id': get_hostname()
    }
    
    # If in production, we always use the local ELK setup
    if environment == 'production':
        elk_config['enabled'] = True
        return elk_config
    
    # If in development, check if remote ELK is enabled
    if environment in ('development', 'staging', 'dev') and is_remote_elk_enabled():
        elk_config['enabled'] = True
    
    return elk_config

def get_filebeat_env_vars():
    """
    Generate environment variables for Filebeat configuration.
    
    Returns a dictionary of environment variables to be set for Filebeat.
    """
    elk_config = configure_elk_logging()
    
    env_vars = {
        'ELASTICSEARCH_HOST': elk_config['host'],
        'ELASTICSEARCH_PORT': elk_config['port'],
        'KIBANA_HOST': os.environ.get('KIBANA_HOST', elk_config['host']),
        'KIBANA_PORT': os.environ.get('KIBANA_PORT', '5601'),
        'ELASTICSEARCH_INDEX_PREFIX': elk_config['index_prefix'],
        'DEVELOPER_ID': elk_config['developer_id'],
        'PYERP_ENV': os.environ.get('PYERP_ENV', 'development')
    }
    
    if elk_config['username']:
        env_vars['ELASTICSEARCH_USERNAME'] = elk_config['username']
        
    if elk_config['password']:
        env_vars['ELASTICSEARCH_PASSWORD'] = elk_config['password']
    
    return env_vars

if __name__ == "__main__":
    # This can be run directly to output configuration or for testing
    config = configure_elk_logging()
    print(f"ELK Configuration: {json.dumps(config, indent=2)}")
    print(f"Remote ELK Enabled: {is_remote_elk_enabled()}")
    print(f"Developer ID (Hostname): {get_hostname()}") 