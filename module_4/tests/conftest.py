import sys
import os
import pytest
import glob
import subprocess
import psycopg
from src.app import create_app
from src.config import DSN



# Add project root to Python path dynamically for test imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def client():
    app = create_app({"TESTING": True})
    os.environ["USE_SAMPLE_HTML"] = "1"
    return app.test_client()

@pytest.fixture(scope="session")
def db_conn():
    """Create a database connection for the entire test session."""
    with psycopg.connect(DSN) as conn:
        yield conn

@pytest.fixture(scope="session")
def populated_db(db_conn, client):
    """Fixture to ensure DB has test data loaded once for the entire test session."""
    # Clean start
    with db_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gradrecords CASCADE")
        cur.execute("TRUNCATE TABLE gradrecords_latest CASCADE")
    db_conn.commit()
    
    # Load data once
    resp = client.post("/fetch-data", follow_redirects=True)
    assert resp.status_code in (200, 302), "Failed to load initial test data"
    
    # Verify data was loaded
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count = cur.fetchone()[0]
        assert count > 0, "No data loaded from fetch-data"
    
    yield db_conn
    
    # Optional: Clean up after all tests complete
    with db_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gradrecords CASCADE")
        cur.execute("TRUNCATE TABLE gradrecords_latest CASCADE")
    db_conn.commit()

def pytest_configure(config):
    os.environ["USE_SAMPLE_HTML"] = "1"

# Cleanup fixture: delete all files in src/data except applicant_data_0.json

@pytest.fixture(autouse=True, scope="session")
def cleanup_data_dir():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/data"))
    print(f"Data directory: {data_dir}")
    keep_file = os.path.join(data_dir, "noname_0.json")
    # No-op before tests
    yield
    # Cleanup after all tests in the module, even if tests fail
    for f in glob.glob(os.path.join(data_dir, "*.json")):
        print(f"Found {f}")
        if os.path.abspath(f) != os.path.abspath(keep_file):
            try:
                print(f"Deleting {f}")
                os.remove(f)
            except Exception as e:
                print(f"Could not delete {f}: {e}")

# Register custom markers for pytest
pytestmark = [
    pytest.mark.db,
    pytest.mark.web,
    pytest.mark.buttons,
    pytest.mark.analysis,
    pytest.mark.integration
]

@pytest.fixture(autouse=True)
def mock_get_db_summary(monkeypatch):
    """Mock get_db_summary to return test data for all tests."""
    def mock_summary(pool):
        return [
            ("Test Question 1?", "Test Answer 1"),
            ("Test Question 2?", "Test Answer 2"),
        ]
    monkeypatch.setattr("src.query_data.get_db_summary", mock_summary)

