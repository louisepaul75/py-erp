"""
Cookie Cache Manager for Legacy API Sessions

This module provides a cache mechanism for storing and retrieving session cookies
used for connecting to the legacy 4D REST API. It helps reduce the number of
server-side sessions by reusing existing valid session cookies.

The implementation uses Django's cache framework if available, a simple file-based
cache for persistence between runs, or falls back to a thread-safe in-memory implementation.
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if file cache is forced via environment variable
FORCE_FILE_CACHE = os.environ.get('FORCE_FILE_CACHE', 'false').lower() in ('true', '1', 'yes')

# Try to import Django's cache framework, fall back to file or local implementation if not available
try:
    from django.core.cache import cache as django_cache
    USING_DJANGO_CACHE = not FORCE_FILE_CACHE
    USING_FILE_CACHE = FORCE_FILE_CACHE
    if USING_DJANGO_CACHE:
        logger.info("Using Django's cache framework for session cookie storage")
    else:
        logger.info("Django available but using file-based cache due to FORCE_FILE_CACHE=true")
except ImportError:
    USING_DJANGO_CACHE = False
    # Use file-based cache by default if not in Django
    USING_FILE_CACHE = True
    logger.info("Django cache not available, using file-based cache for session cookie storage")


class InMemoryCache:
    """
    A simple thread-safe in-memory cache implementation as a fallback
    when Django's cache framework is not available.
    """
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()

    def get(self, key):
        with self._lock:
            # Check if key exists and hasn't expired
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry is None or expiry > time.time():
                    return value
                else:
                    # Clean up expired keys
                    del self._cache[key]
            return None

    def set(self, key, value, timeout=None):
        with self._lock:
            if timeout is not None:
                expiry = time.time() + timeout
            else:
                expiry = None
            self._cache[key] = (value, expiry)

    def delete(self, key):
        with self._lock:
            if key in self._cache:
                del self._cache[key]


class FileCache:
    """
    A file-based cache implementation for persisting data between script executions.
    """
    def __init__(self, cache_dir=None):
        self._lock = threading.RLock()
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Use a .cache directory in the same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.cache_dir = os.path.join(script_dir, '.cache')
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
                logger.info(f"Created cache directory: {self.cache_dir}")
            except Exception as e:
                logger.error(f"Failed to create cache directory: {e}")
                # Fall back to temp directory
                self.cache_dir = os.path.join(os.path.expanduser('~'), '.pyerp_cache')
                if not os.path.exists(self.cache_dir):
                    os.makedirs(self.cache_dir)
                    logger.info(f"Created fallback cache directory: {self.cache_dir}")
    
    def _get_cache_file_path(self, key):
        """Get the file path for a cache key."""
        # Create a safe filename from the key
        safe_key = key.replace(':', '_').replace('/', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key):
        with self._lock:
            file_path = self._get_cache_file_path(key)
            if not os.path.exists(file_path):
                return None
            
            try:
                with open(file_path, 'r') as f:
                    cache_entry = json.load(f)
                
                # Check if expired
                if 'expiry' in cache_entry:
                    expiry = cache_entry['expiry']
                    if expiry is not None and expiry < time.time():
                        # Expired, remove the file
                        os.remove(file_path)
                        return None
                
                return cache_entry['value']
            except Exception as e:
                logger.error(f"Error reading cache file {file_path}: {e}")
                # Remove corrupt file
                try:
                    os.remove(file_path)
                except:
                    pass
                return None
    
    def set(self, key, value, timeout=None):
        with self._lock:
            file_path = self._get_cache_file_path(key)
            
            try:
                cache_entry = {
                    'value': value,
                    'expiry': time.time() + timeout if timeout is not None else None,
                    'created': time.time()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(cache_entry, f)
                
                return True
            except Exception as e:
                logger.error(f"Error writing to cache file {file_path}: {e}")
                return False
    
    def delete(self, key):
        with self._lock:
            file_path = self._get_cache_file_path(key)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting cache file {file_path}: {e}")
            return False


# Create appropriate cache based on availability
if USING_DJANGO_CACHE:
    # Use Django's cache
    pass
elif USING_FILE_CACHE:
    # Use file-based cache
    file_cache = FileCache()
else:
    # Use in-memory cache
    local_cache = InMemoryCache()


class CookieCache:
    """
    Manages caching of session cookies for legacy API connections.
    
    This class provides a unified interface for storing, retrieving, and
    managing session cookies, using either Django's cache framework,
    a file-based cache for persistence, or a fallback in-memory implementation.
    """
    
    # Cookie cache timeout in seconds (1 hour by default)
    DEFAULT_TIMEOUT = 3600
    
    @staticmethod
    def _get_cache_key(environment):
        """
        Generate a unique cache key for the environment.
        
        Args:
            environment (str): The environment identifier ('live' or 'test')
            
        Returns:
            str: A unique cache key
        """
        return f"legacy_api_session_cookie:{environment}"
    
    @staticmethod
    def get_cookie(environment):
        """
        Retrieve a cached session cookie for the given environment.
        
        Args:
            environment (str): The environment to get the cookie for
            
        Returns:
            dict or None: The cached cookie details if found and valid, otherwise None
        """
        cache_key = CookieCache._get_cache_key(environment)
        
        if USING_DJANGO_CACHE:
            cookie_data = django_cache.get(cache_key)
        elif USING_FILE_CACHE:
            cookie_data = file_cache.get(cache_key)
        else:
            cookie_data = local_cache.get(cache_key)
            
        if cookie_data:
            logger.info(f"Retrieved cached session cookie for {environment} environment")
            return cookie_data
        else:
            logger.debug(f"No cached session cookie found for {environment} environment")
            return None
    
    @staticmethod
    def store_cookie(environment, cookie_name, cookie_value, expires_at=None):
        """
        Store a session cookie in the cache.
        
        Args:
            environment (str): The environment identifier ('live' or 'test')
            cookie_name (str): The name of the cookie (e.g., 'WASID4D')
            cookie_value (str): The value of the cookie
            expires_at (datetime, optional): When the cookie expires
            
        Returns:
            bool: True if the cookie was stored successfully
        """
        cache_key = CookieCache._get_cache_key(environment)
        
        # Calculate timeout for the cache entry
        if expires_at:
            now = datetime.now()
            if expires_at > now:
                # Convert timedelta to seconds for the cache
                timeout = int((expires_at - now).total_seconds())
            else:
                # Already expired
                logger.warning(f"Attempted to cache an already expired cookie")
                return False
        else:
            # Use default timeout
            timeout = CookieCache.DEFAULT_TIMEOUT
        
        # Store cookie data in cache
        cookie_data = {
            'name': cookie_name,
            'value': cookie_value,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'cached_at': datetime.now().isoformat()
        }
        
        if USING_DJANGO_CACHE:
            django_cache.set(cache_key, cookie_data, timeout=timeout)
        elif USING_FILE_CACHE:
            file_cache.set(cache_key, cookie_data, timeout=timeout)
        else:
            local_cache.set(cache_key, cookie_data, timeout=timeout)
            
        logger.info(f"Stored session cookie for {environment} environment in cache (expires in {timeout} seconds)")
        return True
    
    @staticmethod
    def invalidate_cookie(environment):
        """
        Invalidate a cached cookie for the given environment.
        
        Args:
            environment (str): The environment identifier
            
        Returns:
            bool: True if the cookie was invalidated, False if no cookie was found
        """
        cache_key = CookieCache._get_cache_key(environment)
        
        # Check if the key exists first
        if USING_DJANGO_CACHE:
            cookie_exists = django_cache.get(cache_key) is not None
            if cookie_exists:
                django_cache.delete(cache_key)
                cookie_invalidated = True
            else:
                cookie_invalidated = False
        elif USING_FILE_CACHE:
            cookie_exists = file_cache.get(cache_key) is not None
            if cookie_exists:
                cookie_invalidated = file_cache.delete(cache_key)
            else:
                cookie_invalidated = False
        else:
            cookie_exists = local_cache.get(cache_key) is not None
            if cookie_exists:
                local_cache.delete(cache_key)
                cookie_invalidated = True
            else:
                cookie_invalidated = False
        
        if cookie_invalidated:
            logger.info(f"Invalidated cached session cookie for {environment} environment")
            return True
        else:
            logger.debug(f"No cached session cookie to invalidate for {environment} environment")
            return False 