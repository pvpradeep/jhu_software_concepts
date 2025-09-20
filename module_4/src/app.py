import os
from time import time
import psycopg
from flask import Flask, abort, render_template, request, url_for, redirect
import time
from query_data import get_db_summary
from load_data import init_db, fetch_new_data
import atexit
from threading import Lock

##Close pool on exit.
atexit.register(lambda: pool.close())

app = Flask(__name__)

#Keep pool open till sigint or close
pool = init_db()

#Control update function  - only on button-click
update_summary = 1

# Track whether a data update (fetch_data) is currently running.
# Protected by a lock so concurrent requests in different threads/processes
# won't corrupt the flag.
update_in_progress = False
update_in_progress_lock = Lock()

@app.before_request
def _set_update_flag_for_fetch():
    """Set the update flag when the fetch_data endpoint starts.

    If a fetch is already in progress, return HTTP 409 (Conflict).
    This prevents multiple concurrent fetch_data operations.
    """
    global update_in_progress
    try:
        # request.endpoint is usually the view function name unless explicitly
        # set with the `endpoint=` parameter in route().
        if request.endpoint == 'fetch_data':
            with update_in_progress_lock:
                if update_in_progress:
                    # 409 Conflict is appropriate for concurrent update attempts.
                    abort(409, description='Data update already in progress')
                update_in_progress = True
    # could not simulate in tests
    except Exception: #pragma: no cover
        # If anything goes wrong inspecting the request, don't block
        # other requests unnecessarily; re-raise after ensuring state.
        raise


@app.after_request
def _clear_update_flag(response):
    """Clear the update flag after fetch_data finishes handling the request."""
    global update_in_progress
    try:
        if request.endpoint == 'fetch_data':
            with update_in_progress_lock:
                update_in_progress = False
    finally:
        return response


@app.before_request
def _block_analysis_during_update():
    """Block update_analysis endpoint while a data update is in progress.

    Returns HTTP 409 (Conflict) if an update is running.
    """
    if request.endpoint == 'update_analysis':
        with update_in_progress_lock:
            if update_in_progress:
                abort(409, description='Cannot run analysis update while data update is in progress')


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
    global update_in_progress
    update_in_progress = True
    
    # Scrape new data and update to db
    fetch_new_data(pool)
    time.sleep(1)  # Simulate delay or allow for async completion

    update_in_progress = False

    # After fetching new data, redirect to summary page (or reload current page)
    return redirect(url_for("summary"))


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    global update_in_progress, update_summary, update_in_progress_lock
    '''
    # Explicitly check the flag here for testability
    with update_in_progress_lock:
        if update_in_progress:
            abort(409, description='Cannot run analysis update while data update is in progress')
            return
    if update_in_progress:
      abort(409, description='Cannot run analysis update while data update is in progress')
      return
    '''
    update_summary = 1
    print("Will recalculate summary")
    return redirect(url_for("summary"))

if __name__ == '__main__': #pragma: no cover
  app.run(host='0.0.0.0', port=8080, debug=True)


## Reference code
