"""
run.py

Entry point to start the Flask application.
Creates the app instance by importing from the package's __init__.py
and runs the server on localhost port 8080.
"""
from myPage import create_app

app = create_app()

if __name__ == "__main__":
    # Run app on localhost port 8080 with debug enabled if desired
    app.run(host='127.0.0.1', port=8080, debug=True)
