"""
Tests for the version module.
"""

import pytest
from unittest.mock import patch


@pytest.mark.unit
class TestVersionModule:
    """Tests for the version module functionality."""

    def test_get_version(self):
        """Test that get_version returns the current version."""
        from pyerp.version import get_version, __version__
        
        # Test that the version returned matches the module's __version__
        assert get_version() == __version__
        assert isinstance(get_version(), str)
        assert len(get_version().split(".")) == 3  # Major.Minor.Patch format
    
    def test_bump_version_patch(self):
        """Test bumping the patch version."""
        with patch('pyerp.version.__version__', '1.2.3'):
            from pyerp.version import bump_version
            
            # Test patch bump (default)
            new_version = bump_version()
            assert new_version == '1.2.4'
            
            # Test explicit patch bump
            new_version = bump_version('patch')
            assert new_version == '1.2.5'
    
    def test_bump_version_minor(self):
        """Test bumping the minor version."""
        with patch('pyerp.version.__version__', '1.2.3'):
            from pyerp.version import bump_version
            
            # Test minor bump
            new_version = bump_version('minor')
            assert new_version == '1.3.0'
    
    def test_bump_version_major(self):
        """Test bumping the major version."""
        with patch('pyerp.version.__version__', '1.2.3'):
            from pyerp.version import bump_version
            
            # Test major bump
            new_version = bump_version('major')
            assert new_version == '2.0.0' 