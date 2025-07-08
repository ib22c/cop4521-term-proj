from flask import Flask, render_template, request
from database import get_db_connection
import psycopg2.extras

app = Flask(__name__)

@app.route('/')
def decision():
    return render_template('index.html')

@app.route('/home')
def home():
    con = get_db_connection()
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""        
        SELECT b.book_id, b.title, b.price, b.image_id, a.author_name
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        WHERE b.price > 10 AND b.price < 20
        ORDER BY b.price ASC
    """)

    books_under_20 = cursor.fetchall()

    cursor.execute("""
        SELECT b.book_id, b.title, b.price, b.image_id, a.author_name
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        WHERE b.price < 10
        ORDER BY b.price ASC           
    """)

    books_under_10 = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template('home.html', books_under_10 = books_under_10, books_under_20 = books_under_20)



if __name__ == '__main__':
    app.run(debug=True)