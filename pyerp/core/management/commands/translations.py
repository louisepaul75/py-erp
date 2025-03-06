"""
Custom management command for translation management tasks.
"""

import os
import re  # noqa: F401
import struct  # noqa: F401
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _  # noqa: F401

try:
    import polib
    POLIB_AVAILABLE = True
except ImportError:
    POLIB_AVAILABLE = False


class Command(BaseCommand):
    help = 'Translation management utilities'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            'action',  # noqa: E128
            choices=['extract', 'compile', 'status', 'update'],  # noqa: F841
            help='Action to perform (extract, compile, status, update)'  # noqa: F841
        )
        parser.add_argument(
            '--locale',  # noqa: E128
            '-l',
            help='Specific locale to work with (e.g., "de" for German). If not specified, all locales will be processed.'  # noqa: E501
        )

    def handle(self, *args, **options):
        action = options['action']
        locale = options.get('locale')

        if action == 'extract':
            self.extract_messages(locale)
        elif action == 'compile':
            self.compile_messages(locale)
        elif action == 'status':
            self.translation_status(locale)
        elif action == 'update':
            self.update_translations(locale)
        else:
            raise CommandError(f"Unknown action: {action}")

    def extract_messages(self, locale=None):
        """Extract messages from source code into .po files."""
        self.stdout.write('Extracting messages...')
        locale_arg = ['-l', locale] if locale else []

        try:
            venv_path = os.environ.get('VIRTUAL_ENV')
            if venv_path:
                python_exe = os.path.join(venv_path, 'Scripts', 'python')
            else:
                python_exe = 'python'

            cmd = [python_exe, 'manage.py', 'makemessages', '--no-location', '--no-obsolete'] + locale_arg  # noqa: E501
            self.stdout.write(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.stderr.write(self.style.ERROR(f"Error extracting messages: {result.stderr}"))  # noqa: E501
                return

            self.stdout.write(self.style.SUCCESS('Messages extracted successfully.'))  # noqa: E501
            self.stdout.write(result.stdout)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error extracting messages: {e}"))  # noqa: E501

    def compile_messages(self, locale=None):
        """Compile .po files into .mo files."""
        self.stdout.write('Compiling messages...')

 # Try using Django's compilemessages first
        try:
            locale_arg = ['-l', locale] if locale else []
            venv_path = os.environ.get('VIRTUAL_ENV')
            if venv_path:
                python_exe = os.path.join(venv_path, 'Scripts', 'python')
            else:
                python_exe = 'python'

            cmd = [python_exe, 'manage.py', 'compilemessages'] + locale_arg
            self.stdout.write(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('Messages compiled successfully using Django.'))  # noqa: E501
                return
            else:
                self.stdout.write(self.style.WARNING('Django compilemessages failed, falling back to Python implementation.'))  # noqa: E501
                self.stdout.write(f"Error was: {result.stderr}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Django compilemessages error: {e}. Falling back to Python implementation.'))  # noqa: E501

 # Fallback: Use Python-based .mo file generation
        self._compile_messages_python(locale)

    def _compile_messages_python(self, locale=None):
        """
        Python-based .po to .mo file compiler.
        Uses polib if available, otherwise falls back to a simpler implementation.  # noqa: E501
        """
        if not POLIB_AVAILABLE:
            self.stdout.write(self.style.WARNING("polib is not installed. Please run 'pip install polib' for better .mo file generation."))  # noqa: E501
            return

        locale_dirs = []

 # Get all locales or specific locale directory
        if locale:
            locale_path = os.path.join(settings.LOCALE_PATHS[0], locale)
            if os.path.exists(locale_path):
                locale_dirs.append((locale, locale_path))
            else:
                self.stderr.write(self.style.ERROR(f"Locale directory not found: {locale_path}"))  # noqa: E501
                return
        else:
            base_locale_path = settings.LOCALE_PATHS[0]
            for item in os.listdir(base_locale_path):
                full_path = os.path.join(base_locale_path, item)
                if os.path.isdir(full_path):
                    locale_dirs.append((item, full_path))

 # Process each locale
        for locale_code, locale_path in locale_dirs:
            po_path = os.path.join(locale_path, 'LC_MESSAGES', 'django.po')
            mo_path = os.path.join(locale_path, 'LC_MESSAGES', 'django.mo')

            if os.path.exists(po_path):
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    self.stdout.write(self.style.SUCCESS(f"Compiled {locale_code} messages to {mo_path}"))  # noqa: E501
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error compiling {po_path}: {e}"))  # noqa: E501
            else:
                self.stderr.write(self.style.WARNING(f"Locale {locale_code}: .po file not found at {po_path}"))  # noqa: E501

    def translation_status(self, locale=None):
        """Show translation status for the project."""
        self.stdout.write('Translation status:')
        locale_dirs = []

 # Get all locales or specific locale directory
        if locale:
            locale_path = os.path.join(settings.LOCALE_PATHS[0], locale)
            if os.path.exists(locale_path):
                locale_dirs.append((locale, locale_path))
            else:
                self.stderr.write(self.style.ERROR(f"Locale directory not found: {locale_path}"))  # noqa: E501
                return
        else:
            base_locale_path = settings.LOCALE_PATHS[0]
            for item in os.listdir(base_locale_path):
                full_path = os.path.join(base_locale_path, item)
                if os.path.isdir(full_path):
                    locale_dirs.append((item, full_path))

 # Process each locale
        for locale_code, locale_path in locale_dirs:
            po_path = os.path.join(locale_path, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_path):
                self.stdout.write(self.style.SUCCESS(f"Locale: {locale_code}"))
                try:
                    with open(po_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        msgid_count = content.count('msgid ')
                        if content.find('msgid ""') == content.find('msgid '):
                            msgid_count -= 1
                        self.stdout.write(f"  - Total messages: {msgid_count}")

 # Try to count fuzzy/untranslated messages
                        fuzzy_count = content.count('#, fuzzy')
                        self.stdout.write(f"  - Fuzzy translations: {fuzzy_count}")  # noqa: E501

 # Check if compiled .mo file exists
                        mo_path = os.path.join(locale_path, 'LC_MESSAGES', 'django.mo')  # noqa: E501
                        mo_status = "Exists" if os.path.exists(mo_path) else "Missing"  # noqa: E501
                        self.stdout.write(f"  - Compiled .mo file: {mo_status}")  # noqa: E501

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  Error analyzing {po_path}: {e}"))  # noqa: E501
            else:
                self.stderr.write(self.style.WARNING(f"Locale {locale_code}: .po file not found at {po_path}"))  # noqa: E501

    def update_translations(self, locale=None):
        """Update .po files with new messages from source code."""
        self.stdout.write('Updating translations...')

 # First extract messages
        self.extract_messages(locale)

 # Then compile messages
        self.compile_messages(locale)

 # Show status
        self.translation_status(locale)

        self.stdout.write(self.style.SUCCESS('Translation files updated successfully.'))  # noqa: E501
