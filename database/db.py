# Handles MYSQL connection and running queries

import mysql.connector
import pandas as pd

# ------------------------------
# SQL Connection
# ------------------------------
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Password',
        database='NEO_DB'
    )

# ------------------------------
# Function to Run Any SQL Query
# ------------------------------
def run_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(result)
