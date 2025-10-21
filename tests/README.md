# Film Calendar Tests

This directory contains tests for the Film Calendar project.

## Running Tests

To run the tests, use pytest:

```bash
# Install dev dependencies
python -m pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage report
pytest --cov=filmcalendar

# Run a specific test file
pytest tests/test_filmcalendar.py

# Run a specific test
pytest tests/test_filmcalendar.py::TestFilmCalendar::test_init
```

## Test Structure

- `test_filmcalendar.py`: Tests for the core `FilmCalendar` class
- `test_theaters.py`: Tests for theater-specific implementations
- `conftest.py`: Pytest configuration and shared fixtures

## Adding New Tests

When adding tests for a new theater implementation:

1. Create a new test class in `test_theaters.py` or a new file if necessary
2. Mock any external requests to avoid network calls during testing
3. Test both normal operation and error handling
4. Follow existing patterns for consistency

## Code Coverage

Aim for high test coverage of the core functionality, especially:

- Calendar creation and manipulation
- Event addition and properties
- Error handling
- File output (ICS and RSS)