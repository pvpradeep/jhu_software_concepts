import os
from time import time
import psycopg
from flask import Flask, abort, render_template, request, url_for, redirect
import time
from src.query_data import get_db_summary
from src.load_data import init_db, fetch_new_data
import atexit
from threading import Lock

def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)

    #Keep pool open till sigint or close
    pool = init_db()
    atexit.register(lambda: pool.close())

    #Control update function  - only on button-click
    update_summary = 1

    # Track whether a data update (fetch_data) is currently running.
    update_in_progress = False
    update_in_progress_lock = Lock()

    @app.before_request
    def _set_update_flag_for_fetch():
        nonlocal update_in_progress
        """Set the update flag when the fetch_data endpoint starts.

        If a fetch is already in progress, return HTTP 409 (Conflict).
        This prevents multiple concurrent fetch_data operations.
        """
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
        nonlocal update_in_progress
        """Clear the update flag after fetch_data finishes handling the request."""
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
        nonlocal update_summary
        """
        Render the summary page with database analysis results.
        
        This function serves as the main route (/) handler that displays summary statistics 
        from the database. It uses a caching mechanism through the update_summary flag to 
        avoid recalculating results on every request.
        
        :return: Rendered summary.html template with query results
        :rtype: flask.Response
        
        Global variables:
            - results: Cached database summary results
            - update_summary: Flag indicating if summary needs recalculation
        """
        if update_summary:
            app.results = get_db_summary(pool)
            update_summary = False
        #close_db(pool)
        return render_template('summary.html', queries=app.results)

    @app.route("/fetch-data", methods=["POST"])
    def fetch_data():
        nonlocal update_in_progress
        """
        Fetch and process new data from GradCafe.
        
        This route handler triggers the scraping of new data and its processing through
        the LLM pipeline. It uses a global flag to prevent concurrent updates and includes
        a small delay to ensure async operations complete.
        
        :return: Redirect to summary page after completion
        :rtype: werkzeug.wrappers.Response
        :raises: HTTP 409 if an update is already in progress (handled by before_request)
        
        Global variables:
            - update_in_progress: Flag indicating active update operation
        """
        update_in_progress = True
        
        # Scrape new data and update to db
        fetch_new_data(pool)
        time.sleep(1)  # Simulate delay or allow for async completion

        update_in_progress = False

        # After fetching new data, redirect to summary page (or reload current page)
        return redirect(url_for("summary"))

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        nonlocal update_summary
        """
        Trigger a recalculation of the database analysis summary.
        
        This route handler sets the update_summary flag to force a recalculation
        of the summary statistics on the next visit to the summary page. Concurrent
        updates are prevented through a before_request handler.
        
        :return: Redirect to summary page to show updated analysis
        :rtype: werkzeug.wrappers.Response
        :raises: HTTP 409 if a data update is in progress (handled by before_request)
        
        Global variables:
            - update_in_progress: Flag checked for concurrent operations
            - update_summary: Flag triggering summary recalculation
            - update_in_progress_lock: Lock for thread-safe operations
        """
        update_summary = 1
        print("Will recalculate summary")
        return redirect(url_for("summary"))

    return app

if __name__ == '__main__': #pragma: no cover
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)


## Reference code
