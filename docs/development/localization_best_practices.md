# Localization Best Practices

This document provides guidelines and best practices for developers working on the pyERP system to ensure proper internationalization and localization of the application.

## General Guidelines

### 1. Text Content

- **Never hardcode user-visible strings**
  - Always use translation functions/tags
  - This includes button labels, error messages, notifications, etc.
  - Even for seemingly "universal" words like "OK" or "Cancel"

- **Use full sentences**
  - Avoid constructing sentences from fragments
  - Example (bad): _('Hello') + ' ' + user.name + '!'
  - Example (good): _('Hello {}!').format(user.name)

- **Provide context for ambiguous terms**
  - Use translation context for words that have multiple meanings
  - Example: `_('March', context='month')` vs `_('March', context='command')`

- **Maintain capitalization consistency**
  - Be consistent with your capitalization in source strings
  - Don't rely on translators to fix capitalization issues

### 2. Variable Text

- **Use named placeholders**
  - Use named placeholders instead of positional ones when possible
  - Example: `_('Hello, %(name)s!') % {'name': user.name}`
  - This makes it easier for translators to reorder words

- **Provide translator comments**
  - Use translator comments to explain the context when needed
  - Example: `# Translators: This appears on the homepage hero banner`

- **Be careful with pluralization**
  - Use Django's pluralization capabilities
  - Example: 
    ```python
    ngettext('%(count)d product found', 
             '%(count)d products found', 
             count) % {'count': count}
    ```

### 3. Non-text Content

- **Localize dates, times, and numbers**
  - Use Django's formatting functions instead of manual formatting
  - Example: `django.utils.formats.date_format(date, 'SHORT_DATE_FORMAT')`

- **Be careful with icons and symbols**
  - Some symbols have different meanings in different cultures
  - Use universal icons where possible
  - Consider providing text alternatives with proper translations

## Code Structure

### 1. Python Code

- **Import translation function at the top**
  ```python
  from django.utils.translation import gettext_lazy as _
  ```

- **Use gettext_lazy for model fields**
  - `gettext_lazy` defers translation until needed
  - Essential for model fields which are evaluated at import time:
  ```python
  class Product(models.Model):
      name = models.CharField(_('Name'), max_length=100)
  ```

- **Use gettext for runtime translations**
  ```python
  from django.utils.translation import gettext as _
  
  def view_function(request):
      message = _('Welcome to our site')
      return render(request, 'template.html', {'message': message})
  ```

- **Set active language when needed**
  ```python
  from django.utils.translation import activate, get_language
  
  # Save current language
  current_language = get_language()
  
  # Switch to a specific language
  activate('de')
  
  # Do something in German
  
  # Restore original language
  activate(current_language)
  ```

### 2. Templates

- **Load i18n at the top of every template**
  ```html
  {% load i18n %}
  ```

- **Use trans tag for simple strings**
  ```html
  <h1>{% trans "Welcome" %}</h1>
  ```

- **Use blocktrans for complex content**
  ```html
  {% blocktrans with name=user.name %}
      Hello {{ name }}, welcome to our site.
  {% endblocktrans %}
  ```

- **Use blocktrans with plural**
  ```html
  {% blocktrans count counter=items|length %}
      There is {{ counter }} item.
  {% plural %}
      There are {{ counter }} items.
  {% endblocktrans %}
  ```

### 3. JavaScript

- **Include the JavaScript catalog**
  ```html
  <script src="{% url 'javascript-catalog' %}"></script>
  ```

- **Use gettext functions**
  ```javascript
  // Simple translation
  const message = gettext('Hello world');
  
  // With placeholders
  const welcome = interpolate(
      gettext('Welcome, %(name)s'), 
      {'name': username}, 
      true
  );
  
  // Pluralization
  const itemCount = ngettext(
      'One item', 
      '%(count)s items', 
      count
  ).replace('%(count)s', count);
  ```

## Translation Process

### 1. Marking Strings for Translation

- Run the makemessages command to extract translatable strings:
  ```bash
  python manage.py makemessages -l de -l en
  ```

- Review the .po files to ensure all strings are properly marked

### 2. Updating Translations

- When adding new features, update translation files:
  ```bash
  python manage.py makemessages -a
  ```

### 3. Testing Translations

- Test the application in all supported languages
- Check for:
  - Untranslated strings
  - Truncated text (text too long for UI element)
  - Broken layouts
  - Incorrect date/number formatting

## Common Mistakes

- **Concatenating translated strings**
  - Problem: Word order differs between languages
  - Solution: Translate whole phrases, use placeholders for variables

- **Hardcoding formatting**
  - Problem: Date/number formats vary by locale
  - Solution: Use Django's formatting functions

- **Not providing context**
  - Problem: Ambiguous terms get mistranslated
  - Solution: Use translation context for clarification

- **Assuming all languages read left-to-right**
  - Problem: Some languages (Arabic, Hebrew) read right-to-left
  - Solution: Use CSS that supports RTL layouts

- **Not escaping user input in translations**
  - Problem: Security vulnerabilities
  - Solution: Use Django's escaping mechanisms or safe filter only when appropriate

## Additional Resources

- [Django Translation Documentation](https://docs.djangoproject.com/en/4.2/topics/i18n/translation/)
- [Django Internationalization Documentation](https://docs.djangoproject.com/en/4.2/topics/i18n/)
- [Django JavaScript Translation Catalog](https://docs.djangoproject.com/en/4.2/topics/i18n/translation/#django.views.i18n.JavaScriptCatalog)
- [Django Model Translation](https://django-modeltranslation.readthedocs.io/) 