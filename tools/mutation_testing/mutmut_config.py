def init():
    """Configure mutmut settings."""
    import os
    import sys

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
    
    # Allow overriding paths_to_mutate via environment variable
    if os.environ.get('PATHS_TO_MUTATE'):
        paths_to_mutate = os.environ.get('PATHS_TO_MUTATE')
    else:
        # Source paths to mutate
        paths_to_mutate = '|'.join(include_paths)
    
    # Allow overriding tests_dir via environment variable
    if os.environ.get('TESTS_DIR'):
        tests_dir = os.environ.get('TESTS_DIR')
    else:
        tests_dir = 'tests/'
    
    # Set up the runner command
    runner = 'python -m pytest'
    
    # Add any additional pytest args
    pytest_args = []
    
    # If specific test file/dir is set, add it to pytest args
    if os.environ.get('TESTS_DIR'):
        pytest_args.append(os.environ.get('TESTS_DIR'))
    
    # Build final runner command
    if pytest_args:
        runner = f"{runner} {' '.join(pytest_args)}"
    
    exclude = '|'.join(exclude_paths)
    
    print(f"Mutmut Configuration:")
    print(f"Paths to mutate: {paths_to_mutate}")
    print(f"Tests dir: {tests_dir}")
    print(f"Runner: {runner}")
    
    return {
        'paths_to_mutate': paths_to_mutate,
        'backup': False,
        'runner': runner,
        'tests_dir': tests_dir,
        'dict_synonyms': 'Struct,Bunch',
        'exclude': exclude,
    } 