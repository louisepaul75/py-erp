"""
Mocks and helpers for testing.
"""
from django.template.loader import get_template as original_get_template
from django.template import Template

MOCK_BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Test{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
"""

def mock_get_template(template_name, *args, **kwargs):
    """Mock template loader that returns a simple base.html for tests."""
    if template_name == 'base.html':
        return Template(MOCK_BASE_TEMPLATE)
    return original_get_template(template_name, *args, **kwargs)