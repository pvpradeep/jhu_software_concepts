import os
import psycopg
from flask import Flask, render_template, request, url_for, redirect
from query_data import get_db_summary
from load_data import init_db, fetch_new_data
import atexit

##Close pool on exit.
atexit.register(lambda: pool.close())

app = Flask(__name__)

def get_db_connection():
  """A function to connect to the database"""
  conn = psycopg.connect(os.environ['DATABASE_URL'])
  return conn

@app.route('/create/', methods=('GET', 'POST'))
def create():
  """A function to create a new course and add to database"""
  if request.method == 'POST':
    id = request.form['id']
    name = request.form['name']
    instructor = request.form['instructor']
    room_number = request.form['room_number']
    print(id, name, instructor, room_number)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO courses(id, name, instructor, room_number)
      VALUES (%s, %s, %s, %s)""",
      (id, name, instructor, room_number)
      )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))
  return render_template('create.html')


pool = init_db()

@app.route('/')
def summary():
  results = get_db_summary(pool)
  #close_db(pool)
  return render_template('summary.html', queries=results)

'''
## did not work - runs at every context teardown(not at ctrl+c/exit).
@app.teardown_appcontext
def deinit_db(exception):
    if pool:
        pool.close()
        print("Database connection pool closed.")
'''

@app.route("/fetch-data", methods=["POST"])
def fetch_data():
    # Call your database update function here
    fetch_new_data(pool)  # Define this function to update your DB

    # After fetching new data, redirect to summary page (or reload current page)
    return redirect(url_for("summary"))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)