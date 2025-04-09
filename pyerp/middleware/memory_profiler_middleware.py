import os
import logging
from pyerp.core import memory_profiler

logger = logging.getLogger(__name__)

# Check if profiling is enabled via environment variable
PROFILING_ENABLED = os.environ.get("ENABLE_MEMORY_PROFILING", "false").lower() == "true"

class MemoryProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        if PROFILING_ENABLED:
            # Configure here maybe okay, but AppConfig.ready is better for Gunicorn
            # memory_profiler.configure_profiler(f"gunicorn_worker_{os.getpid()}")
            logger.info("Memory Profiler Middleware initialized.")
        else:
            logger.debug("Memory Profiler Middleware disabled.")

    def __call__(self, request):
        if PROFILING_ENABLED:
            memory_profiler.take_snapshot_if_needed()

        response = self.get_response(request)

        # Could also take snapshot after response if needed
        # if PROFILING_ENABLED:
        #     memory_profiler.take_snapshot_if_needed() # Or maybe a different frequency

        return response 