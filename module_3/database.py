import os
import psycopg
import psycopg_pool
from psycopg_pool import ConnectionPool
from config import DSN
from load_data import create_db, close_pool, reset_db
from query_data import print_load_summary ,print_query_results


# Initialize connection pool
pool = ConnectionPool(DSN)

def init_db():
    try:
        reset_db(pool)
        create_db(pool)
        print_load_summary(pool)
        print_query_results(pool)

    finally:
        #close_pool(pool)
        print("Database initialization and summary complete.")