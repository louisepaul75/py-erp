import tracemalloc
import sys
from pathlib import Path

# --- Configuration ---
# Default snapshot file path (can be overridden by command-line argument)
DEFAULT_SNAPSHOT_FILE = "memory_snapshots_output/memory_snapshots/snapshot_celery_worker_22_20250409_173533_717916.prof"
TOP_N = 10 # Number of top lines to display
# --- End Configuration ---

def analyze_snapshot(file_path_str: str, top_n: int):
    """Loads a tracemalloc snapshot and prints top memory consumers."""
    file_path = Path(file_path_str)
    if not file_path.is_file():
        print(f"Error: Snapshot file not found at {file_path}")
        sys.exit(1)

    print(f"Loading snapshot from: {file_path}...")
    try:
        snapshot = tracemalloc.Snapshot.load(str(file_path))
        print("Snapshot loaded successfully.")
    except Exception as e:
        print(f"Error loading snapshot: {e}")
        sys.exit(1)

    print(f"\n--- Top {top_n} lines by memory usage ---")
    try:
        # Use 'lineno' for source file/line, 'traceback' for full stack trace
        top_stats = snapshot.statistics('lineno')
        if not top_stats:
            print("No statistics found in the snapshot.")
            return

        total_allocated = sum(stat.size for stat in top_stats) / 1024 / 1024
        print(f"Total allocated size in snapshot: {total_allocated:.2f} MiB")
        print(f"Showing top {min(top_n, len(top_stats))} lines:")

        for index, stat in enumerate(top_stats[:top_n], 1):
            frame = stat.traceback[0]
            # filename:lineno: size KiB (count allocations)
            print(
                f"  #{index}: {frame.filename}:{frame.lineno}: "
                f"{stat.size / 1024:.1f} KiB "
                f"({stat.count} allocs)"
            )
            # Uncomment to print the full traceback for each top line
            # print(f"    Traceback: {' -> '.join(map(str, stat.traceback))}")

    except Exception as e:
        print(f"Error processing statistics: {e}")

if __name__ == "__main__":
    # Allow overriding the file path via command line argument
    if len(sys.argv) > 1:
        snapshot_file = sys.argv[1]
        print(f"Using snapshot file from command line: {snapshot_file}")
    else:
        snapshot_file = DEFAULT_SNAPSHOT_FILE
        print(f"Using default snapshot file: {snapshot_file}")

    analyze_snapshot(snapshot_file, TOP_N) 