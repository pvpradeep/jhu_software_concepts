import pytest
import psycopg
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from config import DSN

@pytest.mark.db
def test_data_loaded_correctly(populated_db):
    """Test that data was loaded correctly into the database."""
    with populated_db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count = cur.fetchone()[0]
        assert count > 0, "Database should not be empty"

@pytest.mark.db
def test_required_fields_not_null(populated_db):
    """Test that required fields are not null in the loaded data."""
    with populated_db.cursor() as cur:
        cur.execute("SELECT * FROM gradrecords")
        rows = cur.fetchall()
        assert len(rows) > 0, "No rows found in database"
        
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
def test_no_duplicate_rows_on_reload(populated_db, client):
    """Test that reloading data does not create duplicate rows."""
    # Get initial count
    with populated_db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count1 = cur.fetchone()[0]
    
    # Try to load data again
    client.post("/fetch-data", follow_redirects=True)
    
    # Check count hasn't changed
    with populated_db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gradrecords")
        count2 = cur.fetchone()[0]
    
    assert count2 == count1, f"Duplicate rows detected: before={count1}, after={count2}"

@pytest.mark.db
def test_schema_of_returned_entry(populated_db):
    """Test that a simple query returns a row matching the gradrecords schema."""
    with populated_db.cursor() as cur:
        cur.execute("SELECT * FROM gradrecords LIMIT 1")
        row = cur.fetchone()
        assert row is not None, "No data in database"
        
        columns = [desc[0] for desc in cur.description]
        # Expected columns from schema in src/load_data.py
        expected = [
            "program", "comments", "date_added", "url", "status", "term",
            "us_or_international", "gpa", "gre", "gre_v", "gre_aw", "degree",
            "llm_generated_program", "llm_generated_university"
        ]
        for col in expected:
            assert col in columns, f"Missing column {col} in gradrecords"
