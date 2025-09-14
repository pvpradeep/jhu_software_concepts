import os
import psycopg
import psycopg_pool
from psycopg_pool import ConnectionPool
from config import DSN
from database_creation import create_db, close_pool, reset_db
from database_queries import summarize_db


# Initialize connection pool
pool = ConnectionPool(DSN)

try:
    reset_db(pool)
    create_db(pool)
    summarize_db(pool)

finally:
    close_pool(pool)
