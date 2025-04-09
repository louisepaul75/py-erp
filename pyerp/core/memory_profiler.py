import os
import tracemalloc
import time
import logging
import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = Path(os.environ.get("MEMORY_SNAPSHOT_DIR", "/app/data/memory_snapshots"))
SNAPSHOT_INTERVAL_SECONDS = int(os.environ.get("MEMORY_SNAPSHOT_INTERVAL", "300")) # Default 5 minutes
TOP_STATS = int(os.environ.get("MEMORY_SNAPSHOT_TOP_STATS", "25"))

_last_snapshot_time = 0
_process_identifier = "unknown"

def configure_profiler(identifier: str):
    """Configure the profiler with a process identifier."""
    global _process_identifier
    _process_identifier = identifier
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Memory profiler configured for process: {_process_identifier}")
    logger.info(f"Snapshots will be saved to: {SNAPSHOT_DIR}")
    logger.info(f"Snapshot interval: {SNAPSHOT_INTERVAL_SECONDS} seconds")
    if not tracemalloc.is_tracing():
        logger.warning("Tracemalloc is not tracing. Did you start Python with -X tracemalloc?")


def take_snapshot_if_needed():
    """Takes a memory snapshot if the interval has passed."""
    global _last_snapshot_time
    if not tracemalloc.is_tracing():
        return # Don't try to snapshot if not tracing

    current_time = time.monotonic()
    if (current_time - _last_snapshot_time) < SNAPSHOT_INTERVAL_SECONDS:
        return

    try:
        logger.info(f"[{_process_identifier}] Taking memory snapshot...")
        snapshot = tracemalloc.take_snapshot()
        _last_snapshot_time = current_time

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = SNAPSHOT_DIR / f"snapshot_{_process_identifier}_{timestamp}.prof"

        snapshot.dump(str(filename))
        logger.info(f"[{_process_identifier}] Memory snapshot saved to {filename}")

        # Optionally log top stats
        log_top_stats(snapshot)

    except Exception as e:
        logger.error(f"[{_process_identifier}] Error taking memory snapshot: {e}", exc_info=True)

def log_top_stats(snapshot):
    """Logs the top memory allocating lines from a snapshot."""
    try:
        stats = snapshot.statistics('lineno')
        logger.info(f"[{_process_identifier}] Top {TOP_STATS} memory usage by line:")
        for index, stat in enumerate(stats[:TOP_STATS], 1):
            frame = stat.traceback[0]
            logger.info(f"  #{index}: {frame.filename}:{frame.lineno}: {stat.size / 1024:.1f} KiB")
            # Log the traceback
            # logger.info(f"    Traceback: {stat.traceback}")

        # Log top diff with previous (if available - requires storing previous snapshot)
        # This might be more useful in dedicated analysis scripts

    except Exception as e:
        logger.error(f"[{_process_identifier}] Error logging top stats: {e}", exc_info=True) 