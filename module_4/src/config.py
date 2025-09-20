# config.py

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
