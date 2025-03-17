# Sync Module Tests

This directory contains the tests for the Sync module of the pyERP system. The tests are designed to ensure that all components of the sync framework function correctly and reliably.

## Test Structure

The tests are organized by the components they test:

- `test_models.py`: Tests for the data models used in the sync system
- `test_pipeline.py`: Tests for the sync pipeline component
- `test_tasks.py`: Tests for the async tasks used for scheduling syncs
- `test_pipeline_factory.py`: Tests for the factory that creates sync pipelines
- `test_base_components.py`: Tests for the base components of the sync system

## Test Fixtures

The test fixtures are defined in `conftest.py` and provide common mock objects and data for testing. These include:

- `sync_source`: A mock SyncSource object
- `sync_target`: A mock SyncTarget object
- `sync_mapping`: A mock SyncMapping object
- `sync_state`: A mock SyncState object
- `sync_log`: A mock SyncLog object
- `sync_log_detail`: A mock SyncLogDetail object
- `test_times`: Timestamps used for testing

## Running the Tests

To run all sync tests:

```bash
cd /path/to/pyERP
pytest tests/backend/sync/
```

To run a specific test file:

```bash
pytest tests/backend/sync/test_models.py
```

To run a specific test:

```bash
pytest tests/backend/sync/test_models.py::test_sync_log_mark_completed
```

## CI/CD Integration

The sync tests are included in the "backend" test group in the CI/CD pipeline. They run automatically on pushes to the `prod` and `dev` branches and on pull requests to these branches.

## Test Coverage

To generate test coverage reports for the sync module:

```bash
pytest tests/backend/sync/ --cov=pyerp.sync --cov-report=html
```

Then open `htmlcov/index.html` in a browser to view the coverage report. 