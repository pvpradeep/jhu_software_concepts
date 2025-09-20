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
	# Patch fetch-data endpoint to simulate a long-running operation
	import sys, os
	sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
	import app as app_module

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
		resp = client.post("/update-analysis", follow_redirects=False)
		t.join()
		assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"


