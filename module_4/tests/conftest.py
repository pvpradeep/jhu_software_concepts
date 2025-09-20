import sys
import os
import pytest
import glob



# Add src folder to Python path dynamically for test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import app

@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    return app.test_client()

# Cleanup fixture: delete all files in src/data except applicant_data_0.json
@pytest.fixture(autouse=True, scope="session")
def cleanup_data_dir():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "./src/data"))
    keep_file = os.path.join(data_dir, "applicant_data_0.json")
    for f in glob.glob(os.path.join(data_dir, "*.json")):
        if os.path.abspath(f) != os.path.abspath(keep_file):
            try:
                os.remove(f)
            except Exception as e:
                print(f"Could not delete {f}: {e}")