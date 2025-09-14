import os
import psycopg
import psycopg_pool


def print_records(records, x = 3, header = None):
  print("" + "="*40)
  print(f"Printing {header} ")
  print("" + "="*40)
  if (len(records) < x):
    x = len(records)

  for i, record in enumerate(records, start=1):
    print(f"Record {i}: {record}")
    if i == x:
      break
    if (len(records) > x):
      print(f"... and {len(records) - x} more records")
  print("" + "="*40)

def summarize_db(pool):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT COUNT(*) FROM gradRecords')
      total_records = cur.fetchone()[0]
      print(f"Total records in gradRecords table: {total_records}")

      cur.execute('SELECT * FROM gradRecords_latest')
      latest_records = cur.fetchall()
      print(f"Total records in gradRecords_latest table: {len(latest_records)}")
      print_records(latest_records, 5, header="records in gradRecords_latest")

      cur.execute('SELECT * FROM gradRecords LIMIT 5')
      sample_records = cur.fetchall()
      print_records(sample_records, 5, header="Sample records from gradRecords")



def output_to_json_file(data, filename):
  with open(filename, 'w') as f:
    json.dump(data, f, indent=4)
  print(f"Data written to {filename}")
