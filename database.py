# database.py - Database Connection and Schema Definition
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # Required for CREATE DATABASE

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

# --- Database Configuration (Load from environment variables) ---
# load sensitive info from environment variables for security
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME') # Default database name
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT', '5432')

def initialize_db():
    """
    Initializes the database by attempting to connect and, if the database
    does not exist, creates it.
    This requires connecting to a default database (like 'postgres') first.
    """
    
    try:
        # Connect to the default 'postgres' database to create our new database
        temp_conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            database='postgres' # Connect to default 'postgres' database initially
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = temp_conn.cursor()

        # Check if the database already exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        exists = cur.fetchone()

        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating it...")
            cur.execute(sql.SQL(f"CREATE DATABASE {DB_NAME};"))
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        cur.close()
        temp_conn.close()

    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL (initialization): {e}")
        print("Please ensure PostgreSQL is running and your DB_USER/DB_PASS are correct.")
        raise e # Re-raise the exception to indicate failure
    except Exception as e:
        print(f"An unexpected error occurred during database initialization: {e}")
        raise e # Re-raise the exception

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a psycopg2 connection object.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        print("Successfully connected to the database.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        print("Please check your database credentials and ensure the database exists.")
        
        raise e # Re-raise the exception for error handling in app.py
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e

def create_tables():
    """
    Creates the necessary tables in the database if they don't already exist.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # SQL statements to create tables based on your schema
        # Using IF NOT EXISTS to prevent errors if tables already exist
        tables_sql = """
        CREATE TABLE IF NOT EXISTS Categories (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(255) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Authors (
            author_id CHAR(32) PRIMARY KEY, -- MD5 hash is 32 chars
            author_name VARCHAR(255) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            condition VARCHAR(50) NOT NULL, -- e.g., 'new', 'used'
            author_id CHAR(32) REFERENCES Authors(author_id), -- FK to Author
            category_id INTEGER REFERENCES Categories(category_id) -- FK to Category
        );

        CREATE TABLE IF NOT EXISTS Inventory (
            product_id INTEGER PRIMARY KEY REFERENCES Products(product_id), -- PK, FK to Product
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        );

        CREATE TABLE IF NOT EXISTS Customers (
            customer_id CHAR(32) PRIMARY KEY, -- MD5 hash
            customer_name VARCHAR(255) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id SERIAL PRIMARY KEY,
            customer_id CHAR(32) REFERENCES Customers(customer_id), -- FK to Customer
            transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(tables_sql)
        conn.commit() # Commit the transaction to save changes
        cur.close()
        print("Tables created or already exist.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        if conn:
            conn.rollback() # Rollback in case of error
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    try:
        initialize_db()
        create_tables()
        print("\nDatabase and tables setup script completed.")
    except Exception as e:
        print(f"\nScript failed: {e}")

