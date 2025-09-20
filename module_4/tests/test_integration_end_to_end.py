
import os
import glob
import pytest
import time

def delete_all_data_files():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/data"))
    for f in glob.glob(os.path.join(data_dir, "*.json")):
        try:
            os.remove(f)
        except Exception as e:
            print(f"Could not delete {f}: {e}")

@pytest.mark.integration
def test_end_to_end_integration(client):
    # 1. Delete all files in src/data/*
    delete_all_data_files()

    # 2. Start with summary page, check fields are empty or 0
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "Summary" in html or "queries" in html
    # Check for empty/zero values (customize as needed)
    assert "0" in html or "No data" in html or "None" in html

    # 3. Fetch new data
    resp = client.post("/fetch-data", follow_redirects=True)
    assert resp.status_code in (200, 302)
    # Wait for data to be processed if needed
    time.sleep(1)

    # 4. Invoke update-analysis
    resp2 = client.post("/update-analysis", follow_redirects=True)
    assert resp2.status_code in (200, 302)
    # Wait for analysis to update
    time.sleep(1)

    # 5. Check that answers have been updated (look for nonzero/nonempty fields)
    response2 = client.get("/")
    html2 = response2.data.decode("utf-8")
    assert "Ans" in html2 or "Analysis" in html2
    # Check for updated values (customize as needed)
    assert "0" not in html2 or "No data" not in html2

    # 6. Delete all files in src/data/* at the end
    delete_all_data_files()
