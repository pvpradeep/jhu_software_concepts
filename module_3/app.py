import os
import psycopg
from flask import Flask, render_template, request, url_for, redirect
from query_data import get_db_summary
from load_data import init_db, fetch_new_data
import atexit

##Close pool on exit.
atexit.register(lambda: pool.close())

app = Flask(__name__)

#Keep pool open till sigint or close
pool = init_db()

#Control update function  - only on button-click
update_summary = 1

@app.route('/')
def summary():
  global results
  global update_summary
  if update_summary:
    results = get_db_summary(pool)
    update_summary = False
  #close_db(pool)
  return render_template('summary.html', queries=results)



@app.route("/fetch-data", methods=["POST"])
def fetch_data():
    # Scrape new data and update to db
    fetch_new_data(pool)
    
    # After fetching new data, redirect to summary page (or reload current page)
    return redirect(url_for("summary"))

@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    global update_summary
    update_summary = 1
    print("Will recalculate summary")
    # Reload current page
    return redirect(url_for("summary"))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)


## Reference code
'''
## did not work - runs at every context teardown(not at ctrl+c/exit).
@app.teardown_appcontext
def deinit_db(exception):
    if pool:
        pool.close()
        print("Database connection pool closed.")
'''  