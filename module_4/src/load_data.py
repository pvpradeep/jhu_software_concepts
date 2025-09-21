import os
import psycopg_pool
import psycopg
from psycopg_pool import ConnectionPool
import json
import time
import subprocess
import glob

from datetime import datetime
from src.query_data import print_load_summary, print_query_results
from src.config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME
from src.query_data import print_records
from src.scrape import scrape_new


MAX_MARKERS = 2

## Convert json to python data types

# "date_added": "April 18, 2025",
def parse_date(date_str):
  return datetime.strptime(date_str, '%B %d, %Y').date()

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default  

# Convert to right data types before inserting in db
# Note order in create-table and convert before inserting should follow schema /(should be identical)
def extract_and_convert(entry):
    return (
        entry.get("program"),
        entry.get("comments"),
        parse_date(entry.get("date_added", "January 1, 1970")),
        entry.get("url"),
        entry.get("status"),
        entry.get("term"),
        entry.get("US/International"),
        safe_float(entry.get("GPA", 0)),
        safe_float(entry.get("GRE", 0)),
        safe_float(entry.get("GRE V", 0)),        
        safe_float(entry.get("GRE AW", 0)),
        entry.get("Degree"),
        entry.get("llm-generated-program"),
        entry.get("llm-generated-university")
    )

def insert_record_from_json(cur, table_name, json_entry):
    values = extract_and_convert(json_entry)
    #print(f"Inserting into {table_name}: {values}")
    insert_sql = f"""
    INSERT INTO {table_name} 
    (program, comments, date_added, url, status, term, us_or_international, gpa, gre, gre_v, gre_aw, degree,
     llm_generated_program, llm_generated_university)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(insert_sql, values)

# Ideally run only first time at startup.
def reset_db(pool):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('DROP TABLE IF EXISTS gradrecords')
      cur.execute('DROP TABLE IF EXISTS gradrecords_latest')
      #order matters due to inheritance
      cur.execute('DROP TABLE IF EXISTS grad_records_common CASCADE')#cascade to drop dependent tables
      conn.commit()
      print("Existing tables dropped.")

"""
Database Schema
=============

The database uses three tables with identical schema through inheritance:
    - grad_records_common: Base table (parent)
    - gradrecords: Main storage table
    - gradrecords_latest: Recent records table

Schema Definition
---------------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column Name
     - Type
     - Description
   * - p_id
     - integer
     - Unique identifier, auto-incrementing primary key
   * - program
     - text
     - University and Department name
   * - comments
     - text
     - User-provided comments about application/decision
   * - date_added
     - date
     - Date when record was added to GradCafe
   * - url
     - text
     - Link to original post on GradCafe
   * - status
     - text
     - Admission decision status
   * - term
     - text
     - Academic term of admission
   * - us_or_international
     - text
     - Student nationality (US/International)
   * - gpa
     - float
     - Student's Grade Point Average
   * - gre
     - float
     - GRE Quantitative score
   * - gre_v
     - float
     - GRE Verbal score
   * - gre_aw
     - float
     - GRE Analytical Writing score
   * - degree
     - text
     - Type of degree program (MS, PhD, etc.)
   * - llm_generated_program
     - text
     - Program name extracted by LLM
   * - llm_generated_university
     - text
     - University name extracted by LLM

Notes:
    - All tables inherit from grad_records_common
    - gradrecords stores the complete dataset
    - gradrecords_latest keeps only recent entries for comparison
"""
create_common_sql = """
CREATE TABLE IF NOT EXISTS grad_records_common (
    id SERIAL PRIMARY KEY,
    program TEXT,
    comments TEXT,
    date_added DATE,    
    url TEXT,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa FLOAT,
    gre FLOAT,
    gre_v FLOAT,    
    gre_aw FLOAT,
    degree TEXT,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);
"""
create_grad_records_sql = "CREATE TABLE IF NOT EXISTS gradrecords (LIKE grad_records_common INCLUDING ALL);"
create_grad_records_latest_sql = "CREATE TABLE IF NOT EXISTS gradrecords_latest (LIKE grad_records_common INCLUDING ALL);"

def create_table():
    """
    Create the database schema for storing grad records.

    Creates three tables in the database:
    - grad_records_common: Base table with common schema (parent table)
    - gradrecords: Main table inheriting from common (stores all records)
    - gradrecords_latest: Table for most recent entries (also inherits from common)

    The function uses table inheritance to maintain schema consistency across tables.
    All tables share the same structure defined in create_common_sql.

    Global variables:
        - pool: Database connection pool used for executing SQL
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            #Dummy, required for table inheritance
            cur.execute(create_common_sql)
            #Actual records table
            cur.execute(create_grad_records_sql)
            #Newest entries records table
            cur.execute(create_grad_records_latest_sql)

            conn.commit()


def insert_grad_records_latest(json_data):
    """
    Update the gradrecords_latest table with the most recent entries.
    
    This function maintains a small set of the most recent records for quick
    comparison during scraping. It first clears the existing entries, then
    inserts up to MAX_MARKERS entries from the new data.
    
    :param json_data: List of grad record entries to process
    :type json_data: list[dict]
    
    Global variables:
        - pool: Database connection pool
        - MAX_MARKERS: Maximum number of recent records to keep
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM gradrecords_latest')
            # Delete all existing entries
            cur.execute('DELETE FROM gradrecords_latest')

            # Insert new entries - upto MAX_MARKERS
            for entry in json_data[:MAX_MARKERS]:
                insert_record_from_json(cur, "gradrecords_latest", entry)
            conn.commit()

      #cur.execute('SELECT * FROM gradrecords_latest')
      #records = cur.fetchall()
      #print_records(records, 2, "new entries in latest")




def insert_grad_records(json_data):
    """
    Insert grad records into both the main and latest tables.
    
    This function coordinates the insertion of records into both the main gradrecords
    table and the gradrecords_latest tracking table. It ensures the most recent
    entries are available for comparison while maintaining the complete dataset.
    
    :param json_data: List of grad record entries to insert
    :type json_data: list[dict]
    
    Global variables:
        - pool: Database connection pool
        - MAX_MARKERS: Used indirectly via insert_grad_records_latest
    """
    # top MAX_MARKERS entries also go to gradrecords_latest table
    insert_grad_records_latest(json_data)

    with pool.connection() as conn:
        with conn.cursor() as cur:
            for entry in json_data:
                insert_record_from_json(cur, "gradrecords", entry)
            conn.commit()



def process_one_json(filename):
    """
    Process a single JSON file and insert its records into the database.
    
    Reads the specified file from the JSON_DATA_FILEPATH directory,
    processes its contents, and inserts the records into the database.
    Handles file not found errors gracefully.
    
    :param filename: Name of the JSON file to process
    :type filename: str
    :return: Total number of records processed
    :rtype: int
    
    Global variables:
        - JSON_DATA_FILEPATH: Directory containing the JSON files
    """
    total_records = 0
    try:
        file_path = os.path.join(JSON_DATA_FILEPATH, f"{filename}")
        with open(file_path, 'r') as f:
            data = json.load(f)
            insert_grad_records(data)
            print(f"Inserted {len(data)} records from {file_path}")      
            total_records += len(data)

    except FileNotFoundError: #pragma: no cover
        print("File not found") 

    finally:
        print(f"Total records added to db: {total_records}")
        return total_records


# Read all matching json data file(s) and insert into the db
def process_json_files():
    """
    Process all JSON data files in sequence and load them into the database.
    
    Searches for files matching the pattern JSON_DATA_FILENAME_{i}.json where i
    starts from 0 and increments until no more files are found. Each file's
    contents are processed and inserted into the database.
    
    :return: Total number of records processed across all files
    :rtype: int
    
    Global variables:
        - JSON_DATA_FILEPATH: Base directory for JSON files
        - JSON_DATA_FILENAME: Base filename pattern for JSON files
    """
    total_records = 0
    i = 0
    while True:
        try:
            file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{i}.json")
            i += 1
            # optimize later to reuse process_one_json.  wont be covered while testing since
            # we load only one file during tests
            with open(file_path, 'r') as f: #pragma: no cover
                data = json.load(f)
                insert_grad_records(data)
                print(f"Inserted {len(data)} records from {file_path}")      
                total_records += len(data)

        except FileNotFoundError:
            break

    print(f"Total records added to db: {total_records}")
    return total_records

# Takes latest records in a json file and adds records to db
# not executed during tests since we load only one file during tests
def load_new_data_to_db(latest_file):
    """
    Process newly scraped data and add it to the database.
    
    This function handles the integration of new data files by:
    1. Finding the next available index in the sequence of data files
    2. Renaming the temporary file to match the sequence
    3. Processing the renamed file's contents into the database
    
    :param latest_file: Path to the temporary file containing new data
    :type latest_file: str
    :return: Number of records processed from the file
    :rtype: int
    
    Global variables:
        - JSON_DATA_FILEPATH: Directory for data files
        - JSON_DATA_FILENAME: Base name for sequenced files
    """
    #rename to right index/ latest index 
    idx = 0
    while True:
        file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{idx}.json")
        idx_exists = os.path.isfile(file_path)
        if idx_exists:  #pragma: no cover
            idx += 1
        else:
            break
    # file_path already points to new name, should try, except errors
    os.rename(latest_file, file_path)
    print(f"{latest_file} renamed to {file_path} successfully.")

    # Add this to db
    return process_one_json(f"{JSON_DATA_FILENAME}_{idx}.json")

# Cleanup temp files after a new fetch
def delete_new_files(folder_path):
    pattern = os.path.join(folder_path, '*_new*')
    files = glob.glob(pattern)
    for file_path in files:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")


# Entry function to scrape new data from gradcafe. stop when it sees known entries, run the llm
# and update db with new records.
def fetch_new_data(pool):
    """
    Orchestrate the complete process of fetching and processing new grad records.
    
    This function manages the entire pipeline of:
    1. Scraping new data from GradCafe
    2. Processing the data through the LLM for entity extraction
    3. Converting data formats (JSON -> JSONL -> cleaned JSON)
    4. Loading processed data into the database
    5. Cleaning up temporary files
    
    :param pool: Database connection pool for database operations
    :type pool: psycopg_pool.ConnectionPool
    :return: None
    
    Global variables:
        - JSON_DATA_FILEPATH: Directory for temporary and permanent data files
    """
    print("Starting fetch...")    
    scrape_new(1, 20) # start from page 1 and stop when it hits a known entry in db
    print("Running llm")
    # New data is in src/data/applicant_data_new.json
    new_json = os.path.join(JSON_DATA_FILEPATH, 'applicant_data_new.json')
    new_jsonl = new_json + '.jsonl'
    new_clean_json = os.path.join(JSON_DATA_FILEPATH, 'applicant_data_new_clean.json')

    #check if new_json exists and has data
    if not os.path.isfile(new_json) or os.path.getsize(new_json) == 0:
        print("No new data fetched.")
        delete_new_files(JSON_DATA_FILEPATH)
        return
    

    # run llm - clean and add macros later.
    llm_app_path = os.path.join(os.path.dirname(__file__), "llm_hosting", "llm_app.py")
    result = subprocess.run(
        ["python", llm_app_path, "--file", new_json],
        capture_output=True, text=True
    )
    print("llm_app.py stdout:", result.stdout)
    print("llm_app.py stderr:", result.stderr)
    if result.returncode == 0:
        print("llm_app.py ran successfully.")
    else: #pragma: no cover
        print(f"llm_app.py failed with return code {result.returncode}")

    # convert jsonl to json (other formats have some issue)
    json_list = []
    with open(new_jsonl, 'r') as jsonl_file:
        for line in jsonl_file:
            json_list.append(json.loads(line))
    with open(new_clean_json, 'w') as json_file:
        json.dump(json_list, json_file, indent=4)

    load_new_data_to_db(new_clean_json)
    delete_new_files(JSON_DATA_FILEPATH)


def create_db(mainPool):
  global pool
  pool = mainPool
  create_table()
  process_json_files()
  
#unused function, currently closing via atexit
def close_pool(pool):  #pragma: no cover
  # Close the pool when done
  pool.close()
  print("Connection pool closed.")

pool = ConnectionPool(DSN)

def init_db():
    """
    Initialize and set up the complete database environment.
    
    This function performs the complete database initialization sequence:
    1. Resets any existing database structure
    2. Creates new tables
    3. Loads initial data
    4. Prints summary statistics and query results
    
    The function uses a connection pool that remains open until program termination
    (handled by atexit).
    
    :return: Initialized database connection pool
    :rtype: psycopg_pool.ConnectionPool
    
    Global variables:
        - pool: Database connection pool
    """
    try:
        reset_db(pool)
        create_db(pool)
        print_load_summary(pool)
        print_query_results(pool)
    
    finally:
        #close_pool(pool)
        print("Database initialization and summary complete.")
        return pool

#Conversion required to compare the records in db against the new one read from gradcafe
def get_grad_records_latest():
    """
    Retrieve the most recent graduate records for comparison.
    
    This function fetches all records from the gradrecords_latest table
    and converts them into a list of dictionaries. This format is used
    for comparing against newly scraped records to avoid duplicates.
    
    :return: List of most recent graduate records
    :rtype: list[dict]
    
    Global variables:
        - pool: Database connection pool
    
    Note:
        The returned dictionaries preserve the database column names as keys,
        making them directly comparable with scraped JSON data.
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM gradrecords_latest")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            
            records = [dict(zip(columns, row)) for row in rows]
        
    return records

