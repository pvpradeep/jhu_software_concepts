import pytest
import threading
import time
from unittest.mock import patch

@pytest.mark.buttons
def test_pull_data_triggers_load(client):
	# Simulate pulling data
	resp = client.post("/fetch-data", follow_redirects=True)
	assert resp.status_code in (200, 302)
	# Check for summary or loaded data in response
	html = resp.data.decode("utf-8").lower()
	assert "summary" in html or "queries" in html or "database analysis" in html

@pytest.mark.buttons
def test_update_analysis_not_busy(client):
	# Should return 200 or 302 when not busy
	resp = client.post("/update-analysis", follow_redirects=True)
	assert resp.status_code in (200, 302)
	html = resp.data.decode("utf-8").lower()
	assert "summary" in html or "queries" in html or "database analysis" in html

@pytest.mark.buttons
def test_update_analysis_while_fetch_in_progress(client):
    """Test that update-analysis is blocked while fetch-data is in progress"""
    event = threading.Event()
    
    def fetch():
        # Start the fetch request and signal that we've begun
        client.post("/fetch-data")
        event.set()
        # Keep the thread alive to simulate long-running operation
        time.sleep(0.5)
    
    # Start fetch in a thread
    t = threading.Thread(target=fetch)
    t.start()
    
    # Wait for fetch operation to start
    event.wait(timeout=1.0)
    
    # Try update-analysis while fetch is still running
    resp = client.post("/update-analysis", follow_redirects=False)
    
    # Clean up
    t.join()
    
    # Should get 409 Conflict since fetch is in progress
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"


