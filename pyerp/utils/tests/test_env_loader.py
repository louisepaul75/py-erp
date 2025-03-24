"""
Tests for the environment variable loader utility.
"""

import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

from pyerp.utils.env_loader import (
    get_project_root,
    get_environment,
    get_settings_module,
    load_environment_variables,
)


@pytest.mark.unit
class TestEnvLoader:
    """Tests for the environment loader functionality."""

    def test_get_project_root(self):
        """Test that get_project_root returns a valid path."""
        root = get_project_root()
        assert isinstance(root, Path)
        assert root.exists()
        assert (root / "pyerp").exists()

    @patch.dict(os.environ, {"PYERP_ENV": "prod"})
    def test_get_environment_from_pyerp_env(self):
        """Test that get_environment uses PYERP_ENV when available."""
        assert get_environment() == "prod"

    @patch.dict(os.environ, {"PYERP_ENV": ""})
    @patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "pyerp.config.settings.production"})
    def test_get_environment_from_settings_prod(self):
        """Test that get_environment uses DJANGO_SETTINGS_MODULE for production."""
        assert get_environment() == "prod"

    @patch.dict(os.environ, {"PYERP_ENV": ""})
    @patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "pyerp.config.settings.development"})
    def test_get_environment_from_settings_dev(self):
        """Test that get_environment uses DJANGO_SETTINGS_MODULE for development."""
        assert get_environment() == "dev"

    @patch.dict(os.environ, {"PYERP_ENV": ""})
    @patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": ""})
    def test_get_environment_default(self):
        """Test that get_environment defaults to 'dev'."""
        assert get_environment() == "dev"

    def test_get_settings_module_prod(self):
        """Test get_settings_module for production."""
        assert get_settings_module("prod") == "pyerp.config.settings.production"

    def test_get_settings_module_test(self):
        """Test get_settings_module for test."""
        assert get_settings_module("test") == "pyerp.config.settings.test"

    def test_get_settings_module_dev(self):
        """Test get_settings_module for development."""
        assert get_settings_module("dev") == "pyerp.config.settings.development"

    def test_get_settings_module_unknown(self):
        """Test get_settings_module for unknown environment defaults to dev."""
        assert get_settings_module("unknown") == "pyerp.config.settings.development"

    @patch("pyerp.utils.env_loader.get_environment")
    def test_get_settings_module_no_arg(self, mock_get_env):
        """Test get_settings_module with no argument."""
        mock_get_env.return_value = "test"
        assert get_settings_module() == "pyerp.config.settings.test"
        mock_get_env.assert_called_once()

    @patch("pyerp.utils.env_loader.get_project_root")
    @patch("pyerp.utils.env_loader.load_dotenv")
    @patch("pathlib.Path.exists")
    def test_load_environment_variables_success(self, mock_exists, mock_load_dotenv, mock_project_root):
        """Test successful loading of environment variables."""
        mock_project_root.return_value = Path("/fake/path")
        # Make the .env.dev file exist
        mock_exists.return_value = True  # Simplified approach
        
        result = load_environment_variables()
        
        assert result is True
        mock_load_dotenv.assert_called_once()
        assert os.environ["PYERP_ENV"] == "dev"
        assert os.environ["DJANGO_SETTINGS_MODULE"] == "pyerp.config.settings.development"

    @patch("pyerp.utils.env_loader.get_project_root")
    @patch("pyerp.utils.env_loader.load_dotenv")
    @patch("pathlib.Path.exists")
    @patch("builtins.print")
    def test_load_environment_variables_verbose(self, mock_print, mock_exists, mock_load_dotenv, mock_project_root):
        """Test verbose output when loading environment variables."""
        mock_project_root.return_value = Path("/fake/path")
        # Make the .env.dev file exist
        mock_exists.return_value = True  # Simplified approach
        
        result = load_environment_variables(verbose=True)
        
        assert result is True
        mock_load_dotenv.assert_called_once()
        mock_print.assert_called()

    @patch("pyerp.utils.env_loader.get_project_root")
    @patch("pyerp.utils.env_loader.load_dotenv")
    @patch("pathlib.Path.exists")
    @patch("builtins.print")
    def test_load_environment_variables_no_file(self, mock_print, mock_exists, mock_load_dotenv, mock_project_root):
        """Test when no environment file is found."""
        mock_project_root.return_value = Path("/fake/path")
        # Make all env files not exist
        mock_exists.return_value = False
        
        result = load_environment_variables(verbose=True)
        
        assert result is False
        mock_load_dotenv.assert_not_called()
        assert mock_print.call_count >= 1  # Warning messages
        assert os.environ["PYERP_ENV"] == "dev"
        assert os.environ["DJANGO_SETTINGS_MODULE"] == "pyerp.config.settings.development" 