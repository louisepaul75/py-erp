import pytest
from unittest import mock
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from pyerp.utils.email_system.utils import (
    _ensure_password_from_1password,
    send_test_email,
    send_html_email,
)


class TestEmailSystemUtils:
    """Tests for the email_system utilities"""

    @mock.patch("pyerp.utils.email_system.utils.get_email_password")
    def test_ensure_password_from_1password_not_enabled(self, mock_get_password):
        """Test that the password is not retrieved when 1Password is not enabled"""
        with mock.patch.object(settings, "EMAIL_USE_1PASSWORD", False):
            result = _ensure_password_from_1password()
            assert result is True
            mock_get_password.assert_not_called()

    @mock.patch("pyerp.utils.email_system.utils.get_email_password")
    def test_ensure_password_from_1password_already_set(self, mock_get_password):
        """Test that the password is not retrieved when already set"""
        with mock.patch.multiple(settings, EMAIL_USE_1PASSWORD=True, EMAIL_HOST_PASSWORD="password"):
            result = _ensure_password_from_1password()
            assert result is True
            mock_get_password.assert_not_called()

    @mock.patch("pyerp.utils.email_system.utils.get_email_password")
    def test_ensure_password_from_1password_no_username(self, mock_get_password):
        """Test that the function returns True when no username is set"""
        with mock.patch.multiple(
            settings, EMAIL_USE_1PASSWORD=True, EMAIL_HOST_PASSWORD="", EMAIL_HOST_USER=""
        ):
            result = _ensure_password_from_1password()
            assert result is True
            mock_get_password.assert_not_called()

    @mock.patch("pyerp.utils.email_system.utils.get_email_password")
    def test_ensure_password_from_1password_success(self, mock_get_password):
        """Test that the password is retrieved successfully"""
        mock_get_password.return_value = "retrieved_password"
        with mock.patch.multiple(
            settings,
            EMAIL_USE_1PASSWORD=True,
            EMAIL_HOST_PASSWORD="",
            EMAIL_HOST_USER="user@example.com",
            EMAIL_1PASSWORD_ITEM_NAME="item_name",
        ):
            result = _ensure_password_from_1password()
            assert result is True
            mock_get_password.assert_called_once_with(
                email_username="user@example.com", item_name="item_name"
            )
            assert settings.EMAIL_HOST_PASSWORD == "retrieved_password"

    @mock.patch("pyerp.utils.email_system.utils.get_email_password")
    def test_ensure_password_from_1password_failure(self, mock_get_password):
        """Test that the function returns False when the password cannot be retrieved"""
        mock_get_password.return_value = None
        with mock.patch.multiple(
            settings,
            EMAIL_USE_1PASSWORD=True,
            EMAIL_HOST_PASSWORD="",
            EMAIL_HOST_USER="user@example.com",
        ):
            result = _ensure_password_from_1password()
            assert result is False
            mock_get_password.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    @mock.patch("pyerp.utils.email_system.utils.render_to_string")
    @mock.patch("pyerp.utils.email_system.utils.EmailMultiAlternatives")
    def test_send_test_email_success(
        self, mock_email_multi_alternatives, mock_render_to_string, mock_ensure_password
    ):
        """Test sending a test email successfully"""
        # Setup mocks
        mock_ensure_password.return_value = True
        mock_render_to_string.return_value = "<html>test</html>"
        mock_msg = mock.MagicMock()
        mock_email_multi_alternatives.return_value = mock_msg

        # Call the function
        result = send_test_email("test@example.com")

        # Assertions
        assert result is True
        mock_ensure_password.assert_called_once()
        mock_render_to_string.assert_called_once()
        mock_email_multi_alternatives.assert_called_once()
        mock_msg.attach_alternative.assert_called_once_with("<html>test</html>", "text/html")
        mock_msg.send.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    def test_send_test_email_password_failure(self, mock_ensure_password):
        """Test sending a test email when password cannot be retrieved"""
        mock_ensure_password.return_value = False
        result = send_test_email("test@example.com")
        assert result is False
        mock_ensure_password.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    @mock.patch("pyerp.utils.email_system.utils.EmailMultiAlternatives")
    def test_send_test_email_exception(self, mock_email_multi_alternatives, mock_ensure_password):
        """Test handling an exception when sending a test email"""
        # Setup mocks
        mock_ensure_password.return_value = True
        mock_msg = mock.MagicMock()
        mock_msg.send.side_effect = Exception("Test exception")
        mock_email_multi_alternatives.return_value = mock_msg

        # Call the function
        result = send_test_email("test@example.com")

        # Assertions
        assert result is False
        mock_ensure_password.assert_called_once()
        mock_email_multi_alternatives.assert_called_once()
        mock_msg.send.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    @mock.patch("pyerp.utils.email_system.utils.EmailMultiAlternatives")
    def test_send_html_email_success(self, mock_email_multi_alternatives, mock_ensure_password):
        """Test sending an HTML email successfully"""
        # Setup mocks
        mock_ensure_password.return_value = True
        mock_msg = mock.MagicMock()
        mock_email_multi_alternatives.return_value = mock_msg

        # Call the function
        result = send_html_email(
            "test@example.com", "Test Subject", "<html>test</html>", attachments=[("file.txt", "content", "text/plain")]
        )

        # Assertions
        assert result is True
        mock_ensure_password.assert_called_once()
        mock_email_multi_alternatives.assert_called_once()
        mock_msg.attach_alternative.assert_called_once_with("<html>test</html>", "text/html")
        mock_msg.attach.assert_called_once_with("file.txt", "content", "text/plain")
        mock_msg.send.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    def test_send_html_email_password_failure(self, mock_ensure_password):
        """Test sending an HTML email when password cannot be retrieved"""
        mock_ensure_password.return_value = False
        result = send_html_email("test@example.com", "Test Subject", "<html>test</html>")
        assert result is False
        mock_ensure_password.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    @mock.patch("pyerp.utils.email_system.utils.EmailMultiAlternatives")
    def test_send_html_email_exception(self, mock_email_multi_alternatives, mock_ensure_password):
        """Test handling an exception when sending an HTML email"""
        # Setup mocks
        mock_ensure_password.return_value = True
        mock_msg = mock.MagicMock()
        mock_msg.send.side_effect = Exception("Test exception")
        mock_email_multi_alternatives.return_value = mock_msg

        # Call the function
        result = send_html_email("test@example.com", "Test Subject", "<html>test</html>")

        # Assertions
        assert result is False
        mock_ensure_password.assert_called_once()
        mock_email_multi_alternatives.assert_called_once()
        mock_msg.send.assert_called_once()

    @mock.patch("pyerp.utils.email_system.utils._ensure_password_from_1password")
    @mock.patch("pyerp.utils.email_system.utils.EmailMultiAlternatives")
    def test_send_html_email_with_cc_bcc(self, mock_email_multi_alternatives, mock_ensure_password):
        """Test sending an HTML email with CC and BCC recipients"""
        # Setup mocks
        mock_ensure_password.return_value = True
        mock_msg = mock.MagicMock()
        mock_email_multi_alternatives.return_value = mock_msg
        
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]

        # Call the function
        result = send_html_email(
            "test@example.com", "Test Subject", "<html>test</html>", cc=cc, bcc=bcc
        )

        # Assertions
        assert result is True
        mock_ensure_password.assert_called_once()
        mock_email_multi_alternatives.assert_called_once_with(
            "Test Subject", 
            "test", 
            settings.DEFAULT_FROM_EMAIL, 
            ["test@example.com"], 
            cc=cc, 
            bcc=bcc
        )
        mock_msg.send.assert_called_once() 