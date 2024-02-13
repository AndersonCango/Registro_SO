import pyodbc
from pyodbc import DatabaseError
from decouple import config

SQL_HOST = config("SQL_HOST")
SQL_DB = config("SQL_DB")
SQL_USER = config("SQL_USER")
SQL_PASS = config("SQL_PASS")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_HOST};"
    f"DATABASE={SQL_DB};"
    f"UID={SQL_USER};"
    f"PWD={SQL_PASS};"
)

def get_connection():
    try:
        return pyodbc.connect(connection_string)
    except DatabaseError as e:
        raise DatabaseError(e) 
