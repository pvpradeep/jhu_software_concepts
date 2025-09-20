import pytest

@pytest.mark.analysis
def test_analysis_format_example(client):
    response = client.get("/")
    assert b"GPA" in response.data or b"Analysis" in response.data



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