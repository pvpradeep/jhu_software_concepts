"""
Configuration Settings for Graduate Application Data Analysis System

This module contains all configuration parameters for the application, including
database connection settings and file path configurations.

Database Configuration
-----------------------
.. data:: DB_HOST
    :type: str
    :value: 'localhost'
    
    Hostname where the PostgreSQL database is running

.. data:: DB_PORT
    :type: int
    :value: 5433
    
    Port number for PostgreSQL database connection

.. data:: DB_NAME
    :type: str
    :value: 'jhudb_gradrec'
    
    Name of the PostgreSQL database

.. data:: DB_USER
    :type: str
    :value: 'jhuuser'
    
    Username for database authentication

.. data:: DSN
    :type: str
    
    Complete database connection string formatted for psycopg

File Path Configuration
------------------------
.. data:: JSON_DATA_FILEPATH
    :type: str
    
    Absolute path to the directory containing JSON data files

.. data:: JSON_DATA_FILENAME
    :type: str
    :value: 'applicant_data'
    
    Base filename for JSON data files. Files are named as
    {JSON_DATA_FILENAME}_{index}.json
"""

DB_HOST = 'localhost'
DB_PORT = 5433
DB_NAME = 'jhudb_gradrec'
DB_USER = 'jhuuser'
DB_PASS = 'jhupassWd'

DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}"

# Data files are ./data/applicant_data.json, ./data/applicant_data_1.json etc
import os
JSON_DATA_FILEPATH = os.path.join(os.path.dirname(__file__), 'data')
JSON_DATA_FILENAME = 'applicant_data'
