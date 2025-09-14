import os
import psycopg_pool
import psycopg
from psycopg_pool import ConnectionPool
import json
from datetime import datetime

from config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME
from database_queries import print_records

MAX_MARKERS = 2

## Conver json to python data types

# "date_added": "April 18, 2025",
def parse_date(date_str):
  return datetime.strptime(date_str, '%B %d, %Y').date()

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default  

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
Database Schema:
p_id        integer Unique iden5fier
program     text University and Department
comments    text Comments
date_added  date Date Added
url         text Link to Post on Grad Café
status      text Admission Status
term        text Start Term
us_or_international text Student na5onality
gpa         float Student GPA
gre         float Student GRE Quant
gre_v       float Student GRE Verbal
gre_aw      float Student Average Wri5ng
degree      float Student Program Degree Type
llm_generated_progr       text LLM Generated Department / Programam
llm_generated_university  text LLM Generated University
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


'''delete current entries in gradrecords_latest and insert new ones'''
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


"""A function to read the json data file(s) and insert into the database"""
def process_json_files():
  total_records = 0
  i = 0
  while True:
    try:
      ##file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{i}.json") if i > 0 else os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}.json")
      file_path = os.path.join(JSON_DATA_FILEPATH, f"{JSON_DATA_FILENAME}_{i}.json")
      i += 1
      with open(file_path, 'r') as f:
        data = json.load(f)
        #print_records(data, 2, "Read from json")  # Print first 2 records for verification
        insert_grad_records(data)
        print(f"Inserted {len(data)} records from {file_path}")      
        total_records += len(data)

    except FileNotFoundError:
      break

  print(f"Total records added to db: {total_records}")


def create_db(mainPool):
  global pool
  pool = mainPool
  create_table()
  process_json_files()
  
def close_pool(pool):  
  # Close the pool when done
  pool.close()
  print("Connection pool closed.")

