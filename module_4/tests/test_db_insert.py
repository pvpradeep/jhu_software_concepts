import pytest
import psycopg
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from config import DSN

@pytest.fixture
def db_conn():
    """Yield a psycopg connection and cleanup after."""
    with psycopg.connect(DSN) as conn:
        yield conn

@pytest.mark.db
@pytest.mark.order(1)
def test_db_empty_before_pull_data(db_conn):
    """Test that gradrecords table is empty before pulling data."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count = cur.fetchone()[0]
        assert count == 0, f"Expected empty gradrecords table, found {count} rows"

@pytest.mark.db
@pytest.mark.order(2)
def test_insert_and_non_null_fields(client, db_conn):
    """Test that after pulling data, new rows exist with non-null required fields."""
    # Trigger data pull
    resp = client.post("/fetch-data", follow_redirects=True)
    assert resp.status_code in (200, 302)
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM gradrecords")
        rows = cur.fetchall()
        assert len(rows) > 0, "No rows inserted after pull-data"
        # Check that required fields are not null in at least one row
        columns = [desc[0] for desc in cur.description]
        idx_gpa = columns.index("gpa")
        idx_program = columns.index("program")
        found = False
        for row in rows:
            if row[idx_gpa] is not None and row[idx_program]:
                found = True
                break
        assert found, "No row with non-null GPA and program"

@pytest.mark.db
def test_no_duplicate_rows_on_reload(client, db_conn):
    """Test that reloading data does not create duplicate rows."""
    # Count rows after first pull
    client.post("/fetch-data", follow_redirects=True)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count1 = cur.fetchone()[0]
    # Pull again
    client.post("/fetch-data", follow_redirects=True)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count2 = cur.fetchone()[0]
    assert count2 == count1, f"Duplicate rows detected: before={count1}, after={count2}"

@pytest.mark.db
def test_schema_of_returned_entry(db_conn):
    """Test that a simple query returns a row matching the gradrecords schema."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM gradrecords LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No data in gradrecords table to check schema")
        columns = [desc[0] for desc in cur.description]
        # Expected columns from schema in src/load_data.py
        expected = [
            "program", "comments", "date_added", "url", "status", "term",
            "us_or_international", "gpa", "gre", "gre_v", "gre_aw", "degree",
            "llm_generated_program", "llm_generated_university"
        ]
        for col in expected:
            assert col in columns, f"Missing column {col} in gradrecords"
