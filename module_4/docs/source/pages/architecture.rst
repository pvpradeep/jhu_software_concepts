Architecture
============

The application is built using a layered architecture with clear separation of concerns:

Web Layer
---------
* Implemented using Flask framework
* Handles HTTP requests and responses
* Renders HTML templates
* Manages user sessions and form data
* Located in ``src/app.py`` and ``src/templates/``

ETL Layer
----------
* Web Scraping (``src/scrape.py``)
    * Fetches data from GradCafe
    * Handles pagination and rate limiting
    * Supports both live scraping and test mode with fixtures

* Data Cleaning (``src/clean.py``)
    * Normalizes raw data
    * Handles missing values
    * Standardizes formats
    * Validates data integrity

* Data Loading (``src/load_data.py``)
    * Manages database connections
    * Handles data insertion and updates
    * Implements data migrations
    * Provides data access methods

Database Layer
--------------
* PostgreSQL database
* Stores processed application data
* Maintains data relationships
* Supports complex queries
* Schema managed through SQLAlchemy

Data Analysis Layer
-------------------
* Query interface (``src/query_data.py``)
* Statistical analysis
* Data aggregation
* Results formatting
* Custom filtering options

Configuration Management
------------------------
* Environment-based configuration
* Database connection settings
* Logging configuration
* Test environment setup