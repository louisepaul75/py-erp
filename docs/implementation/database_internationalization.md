# Database Content Internationalization

This document outlines different approaches for implementing internationalization for database content in the pyERP system.

## Overview

Unlike static content that can be translated using Django's built-in translation system, database content needs special handling for multilingual support. This document compares different approaches and makes recommendations for the pyERP project.

## Comparison of Approaches

### 1. Multiple Fields Approach

**Description:**  
Add language-specific fields for each translatable field in the database model.

**Example:**
```python
class Product(models.Model):
    name = models.CharField(_('Name (German)'), max_length=255)  # Primary language (German)
    name_en = models.CharField(_('Name (English)'), max_length=255, blank=True)
    
    description = models.TextField(_('Description (German)'), blank=True)
    description_en = models.TextField(_('Description (English)'), blank=True)
    
    # Helper methods
    def get_name(self):
        current_lang = get_language()
        if current_lang == 'en' and self.name_en:
            return self.name_en
        return self.name
```

**Advantages:**
- Simple to implement
- Good performance (no additional queries)
- Works with existing Django ORM features
- Supports partial translations (some fields may be translated, others not)
- Easy to fallback to primary language

**Disadvantages:**
- Schema changes required for each new language
- Codebase changes needed for each new language
- Code duplication for accessor methods
- Form handling becomes more complex
- Queries across languages are more complex

### 2. django-modeltranslation

**Description:**  
Use the django-modeltranslation package to automatically create language-specific fields and handle translations.

**Example:**
```python
# Install the package
# pip install django-modeltranslation

# settings.py
INSTALLED_APPS = [
    'modeltranslation',
    # ... other apps
]

# translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Product

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description')

# models.py (original model doesn't change)
class Product(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
```

**Advantages:**
- No manual field additions
- Automatic fallback to primary language
- Admin integration
- No need for custom accessor methods
- Adding new languages doesn't require model changes
- Form handling is simplified

**Disadvantages:**
- More complex setup
- Additional dependency
- Migrations can be tricky
- Less control over schema design
- Potential performance impact for models with many translated fields

### 3. JSON/JSONB Fields

**Description:**  
Store translations in a JSON field with language codes as keys.

**Example:**
```python
class Product(models.Model):
    name_translations = models.JSONField(default=dict)
    description_translations = models.JSONField(default=dict)
    
    @property
    def name(self):
        current_lang = get_language()
        translations = self.name_translations or {}
        return translations.get(current_lang, translations.get('de', ''))
    
    def set_name(self, language_code, value):
        if not self.name_translations:
            self.name_translations = {}
        self.name_translations[language_code] = value
        self.save(update_fields=['name_translations'])
```

**Advantages:**
- Single field for all translations
- No schema changes when adding languages
- Flexible structure for complex translation needs
- Database agnostic (if using standard JSON field)
- Can store translations for multiple fields in one JSON structure

**Disadvantages:**
- More complex querying
- Custom accessor methods required
- Serialization/deserialization overhead
- Less structured than dedicated fields
- MySQL has more limited JSON capabilities than PostgreSQL

### 4. Separate Translation Model

**Description:**  
Create a separate model to store translations with a foreign key to the main model.

**Example:**
```python
class Product(models.Model):
    # Only non-translatable fields
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_translation(self, language_code=None):
        if language_code is None:
            language_code = get_language()
        
        try:
            return self.translations.get(language_code=language_code)
        except ProductTranslation.DoesNotExist:
            # Fall back to default language
            try:
                return self.translations.get(language_code='de')
            except ProductTranslation.DoesNotExist:
                return None

class ProductTranslation(models.Model):
    product = models.ForeignKey(
        Product, related_name='translations', on_delete=models.CASCADE
    )
    language_code = models.CharField(max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('product', 'language_code')
        index_together = ('product', 'language_code')
```

**Advantages:**
- Clean separation of translations
- Easy to add new languages
- No schema changes needed for new languages
- Good for models with many translatable fields
- Efficient for adding/removing languages

**Disadvantages:**
- Additional queries needed to fetch translations
- More complex implementation
- Requires careful handling of joins and prefetch_related
- More complex form handling
- More database tables to maintain

## Recommendation for pyERP

Based on the existing codebase and requirements, we recommend the following approach:

### Short Term (Phase 1): Multiple Fields Approach

**Implementation Details:**
- Continue with the current approach of language-specific fields (`name_en`, `description_en`, etc.)
- Add helper methods like `get_name()` to each model to handle language switching
- Create form fields for each translatable field

**Rationale:**
- Your models already have some fields with this pattern (e.g., `name_en` in `BaseProduct`)
- Simplest to implement quickly
- Good performance characteristics
- Works with your existing data migration code
- Minimizes dependencies

### Medium Term (Phase 2): django-modeltranslation

**Implementation Details:**
- Migrate to django-modeltranslation for core models
- Keep the same database structure but let the library handle translation logic
- Create migration plan to convert existing fields to the library's format

**Rationale:**
- More maintainable as you add more translated fields and languages
- Better integration with Django admin
- Standardized approach with community support
- Reduces code duplication
- Simplifies forms handling

### Long Term (Phase 3): Evaluate Based on Scale

**Considerations:**
- If the number of languages grows significantly, consider the Separate Translation Model approach
- If using PostgreSQL, consider migrating to JSONB fields for better performance
- Evaluate performance impact of translations as the application scales

## Implementation Guidelines

### For Multiple Fields Approach (Short Term)

1. **Model Updates:**
   ```python
   class Product(models.Model):
       # Base fields for primary language (German)
       name = models.CharField(_('Name (German)'), max_length=255)
       description = models.TextField(_('Description (German)'), blank=True)
       
       # English translations
       name_en = models.CharField(_('Name (English)'), max_length=255, blank=True)
       description_en = models.TextField(_('Description (English)'), blank=True)
       
       # Helper method for getting translated content
       def get_name(self):
           current_lang = get_language()
           if current_lang == 'en' and self.name_en:
               return self.name_en
           return self.name
       
       def get_description(self):
           current_lang = get_language()
           if current_lang == 'en' and self.description_en:
               return self.description_en
           return self.description
   ```

2. **Form Handling:**
   ```python
   class ProductForm(forms.ModelForm):
       class Meta:
           model = Product
           fields = ['name', 'name_en', 'description', 'description_en']
   ```

3. **Templates:**
   ```html
   <h1>{{ product.get_name }}</h1>
   <p>{{ product.get_description }}</p>
   ```

### For django-modeltranslation (Medium Term)

1. **Installation:**
   ```bash
   pip install django-modeltranslation
   ```

2. **Settings:**
   ```python
   INSTALLED_APPS = [
       'modeltranslation',  # Must be before admin
       'django.contrib.admin',
       # ... other apps
   ]
   
   LANGUAGES = [
       ('de', _('German')),
       ('en', _('English')),
   ]
   ```

3. **Create Translation Configuration:**
   ```python
   # pyerp/products/translation.py
   from modeltranslation.translator import register, TranslationOptions
   from .models import Product, ProductCategory
   
   @register(Product)
   class ProductTranslationOptions(TranslationOptions):
       fields = ('name', 'description', 'short_description')
   
   @register(ProductCategory)
   class ProductCategoryTranslationOptions(TranslationOptions):
       fields = ('name', 'description')
   ```

4. **Create Migrations:**
   ```bash
   python manage.py makemigrations
   ```

5. **Update Codebase:**
   - Remove custom getter methods
   - Use direct field access in templates
   - Update forms to use the simplified field structure

## Performance Considerations

- **Eager Loading:** When using separate translation models, always use `prefetch_related` to avoid N+1 query problems
- **Caching:** Consider caching translated content, especially for frequently accessed items
- **Indexing:** Add appropriate indexes for language-specific fields
- **Query Optimization:** For filtering by translated fields, create specific indexes or use database features like PostgreSQL's gin/gist indexes for JSON fields

## Migration Considerations

When migrating from one approach to another:

1. **Data Preservation:**
   - Create data migration scripts to convert between formats
   - Always back up data before migrating
   - Test migration on a copy of production data first

2. **Application Changes:**
   - Update all code that accesses the translated fields
   - Update forms and validators
   - Update admin configuration
   - Update API serializers

3. **Testing:**
   - Test all CRUD operations in all supported languages
   - Verify fallback behavior works correctly
   - Test impact on performance and query counts 