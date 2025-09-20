import pytest

@pytest.mark.web
def test_flask_page_example(client):
    response = client.get("/")
    assert response.status_code == 200
