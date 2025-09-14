import os
import psycopg_pool
import psycopg
from psycopg_pool import ConnectionPool
import json

from config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME
from database_queries import print_records

MAX_MARKERS = 2

def reset_db(pool):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('DROP TABLE IF EXISTS gradRecords')
      cur.execute('DROP TABLE IF EXISTS gradRecords_latest')
      conn.commit()
      print("Existing tables dropped.")

def create_table():
  """A function to create tables in the database"""
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('''
        CREATE TABLE IF NOT EXISTS gradRecords (
          id SERIAL PRIMARY KEY,
          data JSONB
        )
      ''')
      #Newest entries records table
      cur.execute('''
        CREATE TABLE IF NOT EXISTS gradRecords_latest (
          id SERIAL PRIMARY KEY,
          data JSONB
        )
      ''')
      conn.commit()


'''delete current entries in gradRecords_latest and insert new ones'''
def insert_grad_records_latest(json_data):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT * FROM gradRecords_latest')
      records = cur.fetchall()
      #print_records(records, 2, "latest to be dropped")  # Adjust x as needed to print more/fewer records
      #print(f"Total records {len(records)} to be dropped in gradRecords_latest")
      # Delete all existing entries
      cur.execute('DELETE FROM gradRecords_latest')

      # Insert new entries - upto MAX_MARKERS
      for entry in json_data[:MAX_MARKERS]:
          cur.execute('INSERT INTO gradRecords_latest (data) VALUES (%s)', [json.dumps(entry)])
          #print(f"Inserted into latest: {entry}")
      conn.commit()

      #cur.execute('SELECT * FROM gradRecords_latest')
      #records = cur.fetchall()
      #print_records(records, 2, "new entries in latest")


def insert_grad_records(json_data):
  # top MAX_MARKERS entries also go to gradRecords_latest table
  insert_grad_records_latest(json_data)

  with pool.connection() as conn:
    with conn.cursor() as cur:
      for entry in json_data:
        cur.execute('INSERT INTO gradRecords (data) VALUES (%s)', [json.dumps(entry)])
      conn.commit()
   

"""
def query_by_name(name_value):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data FROM json_data WHERE data->>%s = %s', ('name', name_value))
            return cur.fetchall()
"""


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
        print_records(data, 2, "Read from json")  # Print first 2 records for verification
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

