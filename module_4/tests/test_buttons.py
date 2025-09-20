import pytest

def test_summary_page_has_buttons(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8").lower()
    assert "pull data" in html, "'pull data' button not found on summary page"
    assert "update summary" in html, "'Update Summary' button not found on summary page"
