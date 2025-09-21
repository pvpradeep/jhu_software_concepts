Installation and Setup
======================

Prerequisites
--------------
* Python 3.13 or higher
* PostgreSQL database
* Virtual environment tool (venv)

Installation Steps
-------------------

1. Clone the repository::

    git clone https://github.com/pvpradeep/jhu_software_concepts.git
    cd module_4

2. Create and activate a virtual environment::

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the package in development mode::

    pip install -e .

4. Install required packages::

    pip install -r requirements.txt
    pip install -r docs/requirements.txt  # for documentation

Environment Variables
---------------------
The following environment variables need to be set:

* ``DATABASE_URL`` - PostgreSQL connection string (e.g., ``postgresql://user:pass@localhost:5432/dbname``)
* ``TEST_ENV`` - Set to "True" when running tests to use test database and fixtures
* ``LOG_LEVEL`` - (Optional) Logging level (default: INFO)

Running the Application
-----------------------
To start the Flask web application::

    python src/app.py

The application will be available at ``http://localhost:5000``