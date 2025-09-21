import re
import pytest

@pytest.mark.analysis
def test_summary_page_includes_ans_label(client):
    """
    Test that the summary page includes the 'Ans' label for each summary line.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    # Count the number of summary lines using data-testid
    num_queries = html.count('data-testid="query-item"')
    # Count the number of 'Ans' labels using data-testid
    num_ans = html.count('data-testid="answer-label"')
    assert num_ans == num_queries, f"Expected {num_queries} 'Ans.' labels, found {num_ans}"

@pytest.mark.analysis
def test_percentages_rounded_to_two_decimals(client):
    """
    Test that any percentage value in the summary is rounded to two decimals.
    """
    response = client.get("/")
    assert response.status_code == 200
    text = response.data.decode("utf-8")
    # Find all percentages in the form of '12.34%' or '100.00%'
    percentages = re.findall(r"(\d+\.\d+)%", text)
    for pct in percentages:
        # Should have exactly two decimals
        decimals = pct.split(".")[1]
        assert len(decimals) == 2, f"Percentage {pct}% is not rounded to two decimals"

@pytest.mark.analysis
def test_query_item_structure(client):
    """
    Test that each query item has the correct structure with required data-testid attributes.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    # Verify the presence of all required elements in each query item
    query_items = html.count('data-testid="query-item"')
    query_texts = html.count('data-testid="query-text"')
    answer_labels = html.count('data-testid="answer-label"')
    
    assert query_items > 0, "No query items found on the page"
    assert query_items == query_texts, f"Expected {query_items} query texts, found {query_texts}"
    assert query_items == answer_labels, f"Expected {query_items} answer labels, found {answer_labels}"

