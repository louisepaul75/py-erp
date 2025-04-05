import subprocess
import sys
import os
# import re # Import regex module  # Removed unused import

def run_sync_command(command_args):
    """Runs Django management command via subprocess, returns True/False."""
    # Correctly locate manage.py at the project root, assuming this script
    # is two levels down (pyerp/sync/scripts) from the root.
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')
    )
    manage_py_path = os.path.join(project_root, 'manage.py')
    command = [sys.executable, manage_py_path] + command_args
    # command_str = ' '.join(command) # Removed unused variable
    print(f"Running: {' '.join(command_args)}...")
    try:
        # Remove capture_output=True and text=True to avoid buffer deadlocks
        # Let the subprocess output stream directly
        # result = subprocess.run(
        #    command, check=True, encoding='utf-8'
        # ) # Removed unused variable
        subprocess.run(command, check=True, encoding='utf-8')
        # --- Temporarily disable output parsing --- 
        # --- as it relied on captured output   ---
        print(f"  SUCCESS: {' '.join(command_args)}")
        # summary = {
        #     "extracted": 0,
        #     "processed": 0,
        #     "transformed": 0,
        #     "created": 0,
        #     "updated": 0,
        #     "skipped": 0,
        #     "failed": 0,
        # }
        # patterns = {
        #     "parent_processed": (
        #         r"Processing finished:.*?Processed=(\d+).*?Created=(\d+)"
        #         r".*?Updated=(\d+).*?Failed=(\d+)"
        #     ),
        #     "run_sync_processed": r"Processed: (\d+)",
        #     "run_sync_created":   r"Created: (\d+)",
        #     "run_sync_updated":   r"Updated: (\d+)",
        #     "run_sync_failed":    r"Failed: (\d+)",
        #     "extracted": r"Extracted (\d+).*(?:parent|child)? records",
        #     "transformed": r"Transformed (\d+).*(?:parent|child)? records",
        #     "load": (
        #         r"(?:load|sync) finished:.*?(\d+) created.*?(\d+) updated"
        #         r".*?(\d+) skipped.*?(\d+) errors"
        #     ),
        # }

        # # Check if result.stdout is available (it won't be if not captured)
        # if hasattr(result, 'stdout') and result.stdout:
        #     for line in result.stdout.splitlines():
        #         matched = False
        #         # Check for parent processed (sync_products style)
        #         match_parent = re.search(
        #             patterns["parent_processed"], line, re.IGNORECASE
        #         )
        #         if match_parent:
        #             summary["processed"] += int(match_parent.group(1))
        #             summary["created"] += int(match_parent.group(2))
        #             summary["updated"] += int(match_parent.group(3))
        #             summary["failed"] += int(match_parent.group(4))
        #             matched = True
        #             continue

        #         # Check for run_sync statistics block lines
        #         match_rsp = re.search(
        #             patterns["run_sync_processed"], line.strip(),
        #             re.IGNORECASE
        #         )
        #         if match_rsp:
        #             summary["processed"] += int(match_rsp.group(1))
        #             matched = True
        #         match_rsc = re.search(
        #             patterns["run_sync_created"], line.strip(), re.IGNORECASE
        #         )
        #         if match_rsc:
        #             summary["created"] += int(match_rsc.group(1))
        #             matched = True
        #         match_rsu = re.search(
        #             patterns["run_sync_updated"], line.strip(), re.IGNORECASE
        #         )
        #         if match_rsu:
        #             summary["updated"] += int(match_rsu.group(1))
        #             matched = True
        #         match_rsf = re.search(
        #             patterns["run_sync_failed"], line.strip(), re.IGNORECASE
        #         )
        #         if match_rsf:
        #             summary["failed"] += int(match_rsf.group(1))
        #             matched = True
        #         if matched: continue

        #         # Check for extraction
        #         match_extract = re.search(
        #             patterns["extracted"], line, re.IGNORECASE
        #         )
        #         if match_extract:
        #             summary["extracted"] += int(match_extract.group(1))
        #             summary["processed"] += int(match_extract.group(1))
        #             continue

        #         # Check for transformation
        #         match_transform = re.search(
        #             patterns["transformed"], line, re.IGNORECASE
        #         )
        #         if match_transform:
        #             summary["transformed"] += int(match_transform.group(1))
        #             continue

        #         # Check for load results
        #         match_load = re.search(patterns["load"], line, re.IGNORECASE)
        #         if match_load:
        #             summary["created"] += int(match_load.group(1))
        #             summary["updated"] += int(match_load.group(2))
        #             summary["skipped"] += int(match_load.group(3))
        #             summary["failed"] += int(match_load.group(4))
        #             continue

        #     # Print summary if any counts were found
        #     if any(summary.values()):
        #         if summary["extracted"] > 0 or summary["transformed"] > 0:
        #             source_summary = (
        #                 f"Extracted={summary['extracted']}, "
        #                 f"Transformed={summary['transformed']}"
        #             )
        #         else:
        #             source_summary = f"Processed={summary['processed']}"

        #         load_summary = (
        #             f"Created={summary['created']}, "
        #             f"Updated={summary['updated']}, "
        #             f"Skipped={summary['skipped']}, "
        #             f"Failed={summary['failed']}"
        #         )

        #         summary_str = f"    Summary: {source_summary}, {load_summary}"
        #         print(summary_str)
        # else:
        #      print(
        #          "    Summary: Output not captured, cannot parse summary."
        #      )
        # --- End Temporarily disable output parsing ---

        return True
    except subprocess.CalledProcessError as e:
        # If output wasn't captured, e.stdout and e.stderr will be None
        print(
            f"  FAILED: {' '.join(command_args)} "
            f"(Exit Code: {e.returncode})"
        )
        if e.stdout:
            print("  --- STDOUT --- ")
            print(e.stdout)
        if e.stderr:
            print("  --- STDERR --- ")
            print(e.stderr)
        # Since output streams directly, it should appear in terminal anyway
        return False
    except FileNotFoundError:
        print(
            f"  FAILED: Could not find manage.py at {manage_py_path} or "
            f"python at {sys.executable}"
        )
        return False
    except Exception as e:
        print(
            f"  FAILED: An unexpected error occurred during "
            f"{' '.join(command_args)}: {e}"
        )
        return False

if __name__ == "__main__":
    print("Starting sync script...")
    print("-" * 20)

    sync_results = {}

    # --- Run Legacy ERP Filter Tests ---
    print("Running Legacy ERP Filter Tests...")
    filter_test_script_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'external_api', 'tests', 'test_legacy_erp_filters.py'
    ))
    filter_test_command = [
        sys.executable, '-m', 'unittest', filter_test_script_path
    ]
    filter_test_success = False
    try:
        # Run with check=True to raise exception on failure
        # Capture output to avoid cluttering the main script's output too much,
        # but print it on failure.
        result = subprocess.run(
            filter_test_command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        # Removed unnecessary f-string, added space before comment
        print("  SUCCESS: Legacy ERP Filter Tests")  # Optional summary print
        # Optional: print test output summary if needed from result.stdout
        filter_test_success = True
    except FileNotFoundError:
        print(f"  FAILED: Test script not found at {filter_test_script_path}")
    except subprocess.CalledProcessError as e:
        print(f"  FAILED: Legacy ERP Filter Tests (Exit Code: {e.returncode})")
        print("  --- Test Output (stdout) ---")
        print(e.stdout)
        print("  --- Test Output (stderr) ---")
        print(e.stderr)
    except Exception as e:
        print(
            f"  FAILED: An unexpected error occurred during filter tests: {e}"
        )

    sync_results['Legacy ERP Filter Tests'] = filter_test_success
    print("-" * 20)

    # --- Product Sync ---
    product_sync_args = ['sync_products', '--top=1', '--debug']
    sync_results[' '.join(product_sync_args)] = run_sync_command(
        product_sync_args
    )

    # --- Future Syncs ---
    # Add calls for other sync commands here once refactored
    # Example (currently commented out):
    # sales_sync_args = ['sync_sales_records', '--top=1']
    # sync_results[' '.join(sales_sync_args)] = run_sync_command(
    #     sales_sync_args
    # )

    # --- Employee Sync (Added) ---
    employee_sync_args = ['sync_employees', '--top=1', '--debug']
    sync_results[' '.join(employee_sync_args)] = run_sync_command(
        employee_sync_args
    )

    # --- Customer Sync (Added) ---
    customer_sync_args = ['sync_customers', '--top=1', '--debug']
    sync_results[' '.join(customer_sync_args)] = run_sync_command(
        customer_sync_args
    )

    # --- Sales Records Sync (Added) ---
    sales_sync_args = ['sync_sales_records', '--top=1', '--debug']
    sync_results[' '.join(sales_sync_args)] = run_sync_command(
        sales_sync_args
    )

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