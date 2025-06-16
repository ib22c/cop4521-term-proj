# db connection and schema creation for PostgreSQL
import os
import psycopg2

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT', '5432')

def initialize_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        database='postgres'
    )
    cursor = conn.cursor()

    cursor.close()
    conn.close()



def get_db_connection():
    conn = None
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    print("Successfully connected to the database.")
    return conn

def create_tables():

    conn = None
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE Category (category_id INT PRIMARY KEY, category_name VARCHAR(100))");
    cursor.execute("CREATE TABLE Author (author_id INT PRIMARY KEY, author_name VARCHAR(100))");
    cursor.execute("CREATE TABLE Student (student_id INT PRIMARY KEY, student_name VARCHAR(100))");

    cursor.execute("CREATE TABLE Book (" +
                "book_id INT PRIMARY KEY, " +
                "title VARCHAR(100), " +
                "author_id INT, " +
                "category_id INT, " +
                "FOREIGN KEY(author_id) REFERENCES Author(author_id), " +
                "FOREIGN KEY(category_id) REFERENCES Category(category_id))");

    cursor.execute("CREATE TABLE Inventory (book_id INT PRIMARY KEY, Quantity INTEGER, FOREIGN KEY(book_id) REFERENCES Book(book_id))");
    cursor.execute("CREATE TABLE student_book_tr (" +
                "transaction_id INT PRIMARY KEY, " +
                "student_id INT, " +
                "book_id INT, " +
                "FOREIGN KEY(student_id) REFERENCES Student(student_id), " +
                "FOREIGN KEY(book_id) REFERENCES Book(book_id))");
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    initialize_db()
    create_tables()


