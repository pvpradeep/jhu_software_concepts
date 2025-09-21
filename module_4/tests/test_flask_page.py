import pytest
import re

@pytest.mark.web
def test_summary_page_includes_analysis_and_ans(client):
    response = client.get("/")
    text = response.data.decode("utf-8")
    assert "Analysis" in text, "'Analysis' not found in summary page text"
    assert re.search(r"\bAns\b", text), "No 'Ans' found in summary page text"


@pytest.mark.web
def test_summary_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Summary" in response.data or b"queries" in response.data

@pytest.mark.web
def test_fetch_data_route(client):
    response = client.post("/fetch-data", follow_redirects=False)
    # Should redirect to summary page (302) or return 409 if already in progress
    assert response.status_code in (302, 409)

@pytest.mark.web
def test_update_analysis_route(client):
    response = client.post("/update-analysis", follow_redirects=False)
    # Should redirect to summary page (302) or return 409 if blocked
    assert response.status_code in (302, 409)

@pytest.mark.web
def test_summary_page_has_buttons(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    # Check for button presence using data-testid
    assert 'data-testid="pull-data-btn"' in html, "Pull Data button not found on summary page"
    assert 'data-testid="update-analysis-btn"' in html, "Update Summary button not found on summary page"
