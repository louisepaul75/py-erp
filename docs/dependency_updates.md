# Dependency Updates

## Summary of Recent Updates

As of February 27, 2025, we've updated several dependencies to ensure compatibility with Python 3.12 and to resolve various issues:

### Major Framework Updates

- **Django**: Upgraded from 4.2.11 to 5.1.6
  - This is a major version upgrade that includes new features and backward-incompatible changes
  - Python 3.10+ is now required (we're using Python 3.12)
  - Updated RemovedInDjango60Warning in pytest settings
  - Successfully passed all system checks and tests

### Core Dependencies

- **Celery**: Updated from 5.3.6 to 5.4.0
- **Django-Celery-Beat**: Updated from 2.5.0 to 2.7.0
- **DRF-YASG**: Updated from 1.21.7 to 1.21.9
- **Python-JSON-Logger**: Updated from 2.0.7 to 3.2.1
- **Whitenoise**: Updated from 6.6.0 to 6.9.0

### Added Dependencies

- **Celery Ecosystem**:
  - kombu==5.4.2
  - billiard==4.2.1
  - amqp==5.3.1
  - vine==5.1.0
  - click-didyoumean==0.3.1
  - click-plugins==1.1.1
  - click-repl==0.3.0
  - python-crontab==3.2.0
  - django-timezone-field==7.1

- **API Documentation**:
  - inflection==0.5.1
  - uritemplate==4.1.1
  - pyyaml==6.0.2

- **Dependency Management**:
  - pip-tools==7.4.1

### Updated Utilities

- **python-dateutil**: Updated from 2.8.2 to 2.9.0.post0
- **pytz**: Updated from 2024.1 to 2025.1

## Known Issues

### psycopg2-binary

The `psycopg2-binary` package requires PostgreSQL development libraries to be installed on the system. If you encounter installation issues, refer to the [Dependency Management Guide](dependency_management.md#known-issues) for solutions.

### Environment Variables

We've identified an issue with environment variables containing comments. All environment variables should now be formatted without comments or additional text. For example:

- Correct: `LOG_FILE_SIZE_LIMIT=2097152`
- Incorrect: `LOG_FILE_SIZE_LIMIT=2097152  # 2MB in bytes`

See the [Environment Variables](dependency_management.md#environment-variables) section in the Dependency Management Guide for more details.

## Next Steps

1. Continue monitoring for compatibility issues with Python 3.12
2. Consider implementing a more robust solution for PostgreSQL dependencies
3. Update the CI/CD pipeline to verify environment variable formatting
4. Document any additional issues encountered during development
