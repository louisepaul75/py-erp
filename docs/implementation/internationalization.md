# Internationalization & Localization Implementation Guide

This document provides technical implementation details for adding multilingual support to the pyERP system.

## 1. Overview

The pyERP system will support multiple languages to serve international users and customers. Initially, the system will support German (primary) and English (secondary), with the ability to add more languages in the future.

## 2. Technical Requirements

### 2.1 Django Configuration

Update the base settings file (`pyerp/config/settings/base.py`) with the following configurations:

```python
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'de'  # Default language as German

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
    # Add more languages as needed
]

# Paths where Django should look for translation files
LOCALE_PATHS = [
    BASE_DIR / 'pyerp' / 'locale',
]

# Middleware for language selection (add after SessionMiddleware)
MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Add this line
    'django.middleware.common.CommonMiddleware',
    # ... other middleware ...
]
```

### 2.2 URL Configuration

Update the main URL configuration (`pyerp/urls.py`) to include language prefix support:

```python
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

# Non-localized URLs
urlpatterns = [
    # URLs that should NOT have language prefix go here
    path('api/', include('api_urls')),  # API URLs usually don't need language prefix
    path('i18n/', include('django.conf.urls.i18n')),  # For language switching
]

# Localized URLs - these will have language prefix
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('products/', include('pyerp.products.urls')),
    # ... other app URLs ...
    prefix_default_language=True  # Include prefix for default language too
)
```

### 2.3 Templates

All templates should consistently use translation tags:

```html
{% load i18n %}

<h1>{% trans "Welcome to pyERP" %}</h1>

<!-- For multi-line or complex translations -->
{% blocktrans %}
  This is a multi-line text that needs
  to be translated as a single unit.
{% endblocktrans %}

<!-- With variables -->
{% blocktrans with user=user.username %}
  Hello {{ user }}, welcome to the system.
{% endblocktrans %}

<!-- With context for ambiguous terms -->
{% trans "May" context "month name" %}
{% trans "May" context "modal verb" %}
```

### 2.4 Language Switcher

Add a language switcher component to the base template (`pyerp/templates/base.html`):

```html
<div class="language-switcher">
  <form action="{% url 'set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.path }}">
    <select name="language" onchange="this.form.submit()">
      {% get_current_language as CURRENT_LANGUAGE %}
      {% get_available_languages as LANGUAGES %}
      {% for lang_code, lang_name in LANGUAGES %}
        <option value="{{ lang_code }}" {% if lang_code == CURRENT_LANGUAGE %}selected{% endif %}>
          {{ lang_name }}
        </option>
      {% endfor %}
    </select>
  </form>
</div>
```

## 3. Translation Workflow

### 3.1 Extracting Messages

To extract translatable strings from the codebase:

```bash
# Make messages for a specific app
python manage.py makemessages -l de -l en -e html,txt,py,email -i venv -i node_modules -d django -i "*/\.*" -i docs -a pyerp/products

# Make messages for all apps
python manage.py makemessages -l de -l en -e html,txt,py,email -i venv -i node_modules -d django -i "*/\.*" -i docs -a
```

### 3.2 Translating Message Files

Edit the `.po` files in each locale directory to provide translations:

Example `.po` file structure:
```
#: pyerp/products/models.py:25
msgid "Product name"
msgstr "Produktname"
```

### 3.3 Compiling Messages

Compile the translations into optimized binary files:

```bash
python manage.py compilemessages
```

## 4. Database Model Strategy

### 4.1 Translatable Fields in Models

For models needing translated content, use language-specific fields:

```python
class Product(models.Model):
    name = models.CharField(_('Name (German)'), max_length=255)  # Primary language (German)
    name_en = models.CharField(_('Name (English)'), max_length=255, blank=True)
    
    description = models.TextField(_('Description (German)'), blank=True)
    description_en = models.TextField(_('Description (English)'), blank=True)
    
    # Helper method to get name in current language
    def get_name(self):
        current_lang = get_language()
        if current_lang == 'en' and self.name_en:
            return self.name_en
        return self.name  # Default to primary language
    
    # Helper method to get description in current language
    def get_description(self):
        current_lang = get_language()
        if current_lang == 'en' and self.description_en:
            return self.description_en
        return self.description  # Default to primary language
```

### 4.2 Alternative: django-modeltranslation

For a more robust solution, consider using django-modeltranslation library:

```python
# Install the package
# pip install django-modeltranslation

# In settings.py
INSTALLED_APPS = [
    # ...
    'modeltranslation',
    # django apps...
]

# Create translation.py in your app
from modeltranslation.translator import register, TranslationOptions
from .models import Product

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description')
```

## 5. JavaScript Internationalization

### 5.1 Configure JavaScript Catalog

Update URLs to include the JavaScript catalog view:

```python
from django.views.i18n import JavaScriptCatalog

urlpatterns += [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
```

### 5.2 Include in Templates

```html
<script src="{% url 'javascript-catalog' %}"></script>
```

### 5.3 Use in JavaScript

```javascript
// Translate strings
const message = gettext('Hello, world!');

// Format dates
const date = new Date();
const formattedDate = django.formats.DATE_FORMAT.format(date);

// Format numbers
const number = 1234.56;
const formattedNumber = django.formats.NUMBER_FORMAT.format(number);
```

## 6. Testing & QA

### 6.1 Testing Checklist

1. **URL Translation**
   - Verify URL patterns work with language prefixes
   - Test language switching maintains the correct page

2. **Interface Translation**
   - Check all visible text elements in each supported language
   - Verify form labels, buttons, and error messages

3. **Dynamic Content**
   - Test database content appears in the correct language
   - Verify fallback mechanisms when translations are missing

4. **Data Formatting**
   - Test date/time formats in each language
   - Verify number and currency formatting

5. **Layout Issues**
   - Check for text overflow with longer translated strings
   - Verify RTL layout support if applicable

### 6.2 Automated Tests

Create automated tests for language switching and translation loading:

```python
from django.test import TestCase, Client
from django.urls import reverse

class I18nTests(TestCase):
    def test_language_switching(self):
        # Test switching languages
        c = Client()
        
        # Default language (German)
        response = c.get(reverse('products:product_list'))
        self.assertContains(response, 'Produkte')  # German word
        
        # Switch to English
        response = c.get(reverse('products:product_list'), HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(response, 'Products')  # English word
```

## 7. Deployment Considerations

- Ensure all `.mo` files are compiled and included in the deployment
- Configure the web server to handle URLs with language prefixes
- Set appropriate content-language HTTP headers
- Consider CDN caching strategies for multi-language content

## 8. Ongoing Maintenance

- Establish a process for updating translations when new features are added
- Create guidelines for developers to mark all user-facing strings for translation
- Set up regular validation to catch missing translations
- Document language-specific testing procedures for QA team 