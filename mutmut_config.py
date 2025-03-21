def init():
    """Configure mutmut settings."""
    import os

    # Define directories/files to include for mutation testing
    include_paths = [
        'pyerp/',
        'scripts/',
    ]
    
    # Define directories/files to exclude from mutation testing
    exclude_paths = [
        '__pycache__',
        'migrations',
        'settings',
        'tests',
        'test_*.py',
        '*_test.py',
        'wsgi.py',
        'asgi.py',
        'manage.py',
    ]
    
    # Source paths to mutate
    include = '|'.join(include_paths)
    exclude = '|'.join(exclude_paths)
    
    return {
        'paths_to_mutate': include,
        'backup': False,
        'runner': 'python -m pytest',
        'tests_dir': 'tests/',
        'dict_synonyms': 'Struct,Bunch',
        'exclude': exclude,
    } 