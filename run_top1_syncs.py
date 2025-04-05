import subprocess
import sys
import os

def run_sync_command(command_args):
    """Runs a Django management command using subprocess, returns True/False."""
    manage_py_path = os.path.join(os.path.dirname(__file__), 'manage.py')
    command = [sys.executable, manage_py_path] + command_args
    command_str = ' '.join(command)
    print(f"Running: {' '.join(command_args)}...") # Simplified command name
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        # Print limited success output, maybe last few lines or a summary if available
        # For now, just a simple success message
        print(f"  SUCCESS: {' '.join(command_args)}")
        # Optional: print result.stdout[-500:] # Print last 500 chars of output
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAILED: {' '.join(command_args)} (Exit Code: {e.returncode})")
        print("  --- STDOUT --- ")
        print(e.stdout)
        print("  --- STDERR --- ")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"  FAILED: Could not find manage.py at {manage_py_path} or python at {sys.executable}")
        return False
    except Exception as e:
        print(f"  FAILED: An unexpected error occurred during {' '.join(command_args)}: {e}")
        return False

if __name__ == "__main__":
    print("Starting sync script...")
    print("-" * 20)
    
    sync_results = {}

    # --- Product Sync ---
    product_sync_args = ['sync_products', '--top=1']
    sync_results[' '.join(product_sync_args)] = run_sync_command(product_sync_args)
    
    # --- Future Syncs ---
    # Add calls for other sync commands here once refactored
    # Example (currently commented out):
    # sales_sync_args = ['sync_sales_records', '--top=1']
    # sync_results[' '.join(sales_sync_args)] = run_sync_command(sales_sync_args)
    
    # --- Employee Sync (Added) ---
    employee_sync_args = ['sync_employees', '--top=1']
    sync_results[' '.join(employee_sync_args)] = run_sync_command(employee_sync_args)

    # --- Summary --- 
    print("-" * 20)
    print("Sync Script Summary:")
    all_success = True
    for command, success in sync_results.items():
        status = "PASSED" if success else "FAILED"
        print(f"  - {command}: {status}")
        if not success:
            all_success = False
            
    print("-" * 20)
    if all_success:
        print("All syncs completed successfully.")
    else:
        print("One or more syncs failed.")
    print("Sync script finished.") 