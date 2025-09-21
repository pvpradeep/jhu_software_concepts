import sys
import os
import pytest
import glob
import subprocess



# Add project root to Python path dynamically for test imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from src.app import app

@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    os.environ["USE_SAMPLE_HTML"] = "1"
    return app.test_client()


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

