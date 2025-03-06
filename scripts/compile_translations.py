"""
Standalone script to compile translation files.
"""

import os

import polib


def compile_translations():
    """Compile all .po files to .mo files using polib."""
    print("Compiling translation files...")

    base_path = os.path.join("pyerp", "locale")
    if not os.path.exists(base_path):
        print(f"Error: Path {base_path} does not exist.")
        return

    locales = [
        d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))
    ]

    for locale in locales:
        po_path = os.path.join(base_path, locale, "LC_MESSAGES", "django.po")
        mo_path = os.path.join(base_path, locale, "LC_MESSAGES", "django.mo")

        if not os.path.exists(po_path):
            print(f"Warning: {po_path} does not exist, skipping.")
            continue

        try:
            print(f"Processing {po_path}...")
            po = polib.pofile(po_path)
            po.save_as_mofile(mo_path)
            print(f"Successfully compiled {mo_path}")
        except Exception as e:
            print(f"Error compiling {po_path}: {e}")

    print("Translation compilation completed.")


if __name__ == "__main__":
    compile_translations()
