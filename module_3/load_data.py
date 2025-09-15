import os
import psycopg_pool
import psycopg
from psycopg_pool import ConnectionPool
import json
import time
import subprocess
import glob

from datetime import datetime
from query_data import print_load_summary ,print_query_results

from config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME
from query_data import print_records
from scrape import scrape_new


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

'''
      Database Schema

p_id                integer   Unique iden5fier
program             text      University and Department
comments            text      Comments
date_added          date      Date Added
url                 text      Link to Post on Grad Café
status              text      Admission Status
term                text      Start Term
us_or_international text      Student na5onality
gpa                 float     Student GPA
gre                 float     Student GRE Quant
gre_v               float     Student GRE Verbal
gre_aw              float     Student Average Wri5ng
degree              float     Student Program Degree Type
llm_generated_progr text      LLM Generated Department / Programam
llm_generated_university text LLM Generated University
'''
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
  """A function to create tables in the database"""
  with pool.connection() as conn:
    with conn.cursor() as cur:
      #Dummy, required for table inheritance
      cur.execute(create_common_sql)
      #Actual records table
      cur.execute(create_grad_records_sql)
      #Newest entries records table
      cur.execute(create_grad_records_latest_sql)

      conn.commit()


#Delete current entries in gradrecords_latest and insert new ones
def insert_grad_records_latest(json_data):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT * FROM gradrecords_latest')
      #records = cur.fetchall()
      #print_records(records, 2, "latest to be dropped")  # Adjust x as needed to print more/fewer records
      #print(f"Total records {len(records)} to be dropped in gradrecords_latest")
      # Delete all existing entries
      cur.execute('DELETE FROM gradrecords_latest')

      # Insert new entries - upto MAX_MARKERS
      for entry in json_data[:MAX_MARKERS]:
          insert_record_from_json(cur, "gradrecords_latest", entry)
          #cur.execute('INSERT INTO gradrecords_latest (data) VALUES (%s)', [json.dumps(entry)])
          #print(f"Inserted into latest: {entry}")
      conn.commit()

      #cur.execute('SELECT * FROM gradrecords_latest')
      #records = cur.fetchall()
      #print_records(records, 2, "new entries in latest")




def insert_grad_records(json_data):
  # top MAX_MARKERS entries also go to gradrecords_latest table
  insert_grad_records_latest(json_data)

  with pool.connection() as conn:
    with conn.cursor() as cur:
      for entry in json_data:
          insert_record_from_json(cur, "gradrecords", entry)
          #cur.execute('INSERT INTO gradrecords (data) VALUES (%s)', [json.dumps(entry)])
      conn.commit()



def process_one_json(filename):
  total_records = 0
  try:
    file_path = os.path.join(JSON_DATA_FILEPATH, f"{filename}")
    with open(file_path, 'r') as f:
      data = json.load(f)
      #print_records(data, 2, "Read from json")  # Print first 2 records for verification
      insert_grad_records(data)
      print(f"Inserted {len(data)} records from {file_path}")      
      total_records += len(data)

  except FileNotFoundError:
    print("File not found") 

  finally:
    print(f"Total records added to db: {total_records}")


# Read all matching json data file(s) and insert into the db
def process_json_files():
  total_records = 0
  i = 0
  while True:
    try:
      file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{i}.json")
      i += 1
      # optimize later to reuse process_one_json
      with open(file_path, 'r') as f:
        data = json.load(f)
        #print_records(data, 2, "Read from json")  # Print first 2 records for verification
        insert_grad_records(data)
        print(f"Inserted {len(data)} records from {file_path}")      
        total_records += len(data)

    except FileNotFoundError:
      break

  print(f"Total records added to db: {total_records}")

# Takes latest records in a json file and adds records to db
def load_new_data_to_db(latest_file):
  #rename to right index/ latest index 
  idx = 0
  while True:
    file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{idx}.json")
    idx_exists = os.path.isfile(file_path)
    if idx_exists:
      idx += 1
    else:
        break
   # file_path already points to new name, should try, except errors
  os.rename(latest_file, file_path)
  print(f"{latest_file} renamed to {file_path} successfully.")

  # Add this to db
  process_one_json(f"{JSON_DATA_FILENAME}_{idx}.json")

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
    print("Starting fetch...")    
    scrape_new(1, 400) # start from page 1 and stop when it hits a known entry in db
    print("Running llm")
    #New data is in ./data/applicant_data_new.json

    # run llm - clean and add macros later.
    result = subprocess.run([
      "python", "./llm_hosting/llm_app.py", "--file", "./data/applicant_data_new.json"],
      capture_output=True, text=True)
    print(result.stdout)

    #convert jsonl to json (other formats have some issue)
    json_list = []
    with open('./data/applicant_data_new.json.jsonl', 'r') as jsonl_file:
      for line in jsonl_file:
          json_list.append(json.loads(line))
    with open('./data/applicant_data_new_clean.json', 'w') as json_file:
      json.dump(json_list, json_file, indent=4)

    load_new_data_to_db("./data/applicant_data_new_clean.json")
    delete_new_files("./data")


def create_db(mainPool):
  global pool
  pool = mainPool
  create_table()
  process_json_files()
  
def close_pool(pool):  
  # Close the pool when done
  pool.close()
  print("Connection pool closed.")

pool = ConnectionPool(DSN)

def init_db():
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
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT * FROM gradrecords_latest")
      rows = cur.fetchall()
      columns = [desc[0] for desc in cur.description]
      
      records = [dict(zip(columns, row)) for row in rows]
    
  return records

