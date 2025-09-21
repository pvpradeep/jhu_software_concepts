Testing Guide
==============

Running Tests
-------------
To run the full test suite with coverage::

    pytest --cov=src/ -v

To run specific test files::

    pytest tests/test_flask_page.py -v  # Run web interface tests
    pytest tests/test_db_insert.py -v   # Run database tests

Test Categories
---------------

Integration Tests
~~~~~~~~~~~~~~~~~
* ``test_integration_end_to_end.py`` - Full system integration tests
* Requires database connection
* Tests complete data flow from scraping to web display

UI Tests
~~~~~~~~
* ``test_flask_page.py`` - Flask route and template tests
* ``test_buttons.py`` - UI interaction tests
* Uses pytest-flask for testing Flask applications

Data Processing Tests
~~~~~~~~~~~~~~~~~~~~~
* ``test_analysis_format.py`` - Data formatting and analysis tests
* ``test_db_insert.py`` - Database operation tests

Test Fixtures
--------------
* ``conftest.py`` - Shared pytest fixtures
* ``sample_page.html`` - Mock GradCafe page for offline testing

Key Fixtures:
~~~~~~~~~~~~~
* ``test_client`` - Flask test client
* ``test_database`` - Test database connection
* ``sample_data`` - Sample application data
* ``mock_scraper`` - Mocked web scraper

Test Environment
----------------
Set up test environment::

    export TEST_ENV=True
    export DATABASE_URL=postgresql://user:localhost:5432/test_db

Test Markers
-------------
Available pytest markers::

    @pytest.mark.webtest - Web interface tests
    @pytest.mark.dbtest - Database tests
    @pytest.mark.slow - Time-intensive tests

Run marked tests::

    pytest -v -m webtest  # Run only web tests
    pytest -v -m "not slow"  # Skip slow tests

Coverage Reports
----------------
Generate HTML coverage report::

    pytest --cov=src/ --cov-report=html

Report will be available in ``htmlcov/index.html``