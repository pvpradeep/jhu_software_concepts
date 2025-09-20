import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import threading
import time
import app as app_module


def test_summary_page(client):
    response = client.get("/")
    assert response.status_code == 200
    # Check for presence of queries or summary content in the rendered HTML
    assert b"queries" in response.data or b"Summary" in response.data

def test_fetch_data_route(client):
    response = client.post("/fetch-data", follow_redirects=True)
    # Accept either a successful redirect or a 409 Conflict if update is in progress
    assert response.status_code in (200, 409)
    if response.status_code == 409:
        assert b"already in progress" in response.data

def test_update_analysis_route(client):
    response = client.post("/update-analysis", follow_redirects=True)
    # Accept either a successful redirect or a 409 Conflict if update is in progress
    assert response.status_code in (200, 409)
    if response.status_code == 409:
        assert b"Cannot run analysis update" in response.data

def test_summary_values_rounded(client):
    """
    Ensure all calculated values in the summary are rounded to two decimal places.
    """
    response = client.get("/")
    assert response.status_code == 200
    text = response.data.decode("utf-8")
    import re
    # Find all numbers with more than two decimals in the summary output
    # Accepts numbers like 12.34, 0.00, 100.00, but not 12.345
    # Only checks numbers in the context of GPA, GRE, percentage, etc.
    pattern = re.compile(r"(\d+\.\d{3,})")
    matches = pattern.findall(text)
    assert not matches, f"Found values with more than two decimals: {matches}"

def test_update_analysis_while_fetch_in_progress(client):
    """
    Start fetch-data in a thread, then call update-analysis while fetch is in progress.
    update-analysis should return 409.
    """
    # Patch fetch-data endpoint to simulate a long-running operation
    from unittest.mock import patch

    def slow_fetch_data(*args, **kwargs):
        time.sleep(1)
        return app_module.fetch_data.__wrapped__(*args, **kwargs) if hasattr(app_module.fetch_data, '__wrapped__') else ("done", 200)

    with patch.object(app_module, 'fetch_data', side_effect=slow_fetch_data):
        # Start fetch-data in a thread
        def fetch():
            client.post("/fetch-data")
        t = threading.Thread(target=fetch)
        t.start()
        time.sleep(0.2)  # Give fetch-data time to acquire the in-progress flag
        # Now try update-analysis
        resp = client.post("/update-analysis")
        t.join()
        assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"
