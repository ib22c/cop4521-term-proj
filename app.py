from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
import psycopg2.extras
from auth import create_user, authenticate_user


app = Flask(__name__)
app.secret_key = 'wubahubalub3456765' #no one guessing ts


def check_auth():
    return 'user_id' in session

def require_auth():
    if not check_auth():
        return redirect(url_for('signup'))
    return None

def general_auth():
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

@app.route('/')
def decision():
    if check_auth():
        return redirect(url_for('home'))
    else:
        return redirect(url_for('signup'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')        
        password = request.form.get('password')

        if not all([email, first_name, last_name, password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        user_id, message = create_user(email, first_name, last_name, password)

        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['first_name'] = first_name

            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash(message, 'error')
            return render_template('signup.html')
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            flash('Logged in successfully')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('signup'))

@app.route('/home')
def home():

    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

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

#this is similar to a React component, it will be used across the webiste
#when a user clicks on a book, this will flash
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect
    
    con = get_db_connection()
    cur = con.cur(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT b.book_id, b.title, b.price, b.image_id, a.author_name, c.category_name
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        JOIN Category c ON b.category_id = c.category_id
        WHERE b.book_id = %s
    """, (book_id,))

    book = cur.fetchone()
    cur.close()
    con.close()

    if not book:
        flash('Book not found')
        return redirect(url_for('home'))
    
    return render_template('book_detail.html', book=book)

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))

    con = get_db_connection()
    cur = con.cursor()

    try:
        #check if item is in cart
        cur.execute("SELECT quantity FROM Cart WHERE user_id = %s AND book_id = %s", 
                      (user_id, book_id))
        existing = cur.fetchone()

        if existing:
            new_quantity = existing[0] + quantity
            cur.execute("UPDATE Cart SET quantity = %s WHERE user_id = %s AND book_id = %s",
                          (new_quantity, user_id, book_id))
        else:
            #add new book to cart
            cur.execute("INSERT INTO Cart (user_id, book_id, quantity) VALUES (%s, %s, %s)",
                          (user_id, book_id, quantity))
        con.commit()
        cur.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
        title = cur.fetchone()
        flash(f'{title} added to cart!')
    
    except Exception as e:
        con.rollback()
        flash('Error adding to cart', 'error')
    finally:
        cur.close()
        con.close()

    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/cart')
def view_cart():
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

    user_id = session['user_id']
    con = get_db_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT c.cart_id, c.quantity, b.book_id, b.title, b.price, b.image_id, a.author_name,
               (c.quantity * b.price) as item_total
        FROM Cart c
        JOIN Book b ON c.book_id = b.book_id
        JOIN Author a ON b.author_id = a.author_id
        WHERE c.user_id = %s
        ORDER BY c.added_at DESC
    """, (user_id,))

    cart_items = cur.fetchall()

    total = sum(item['item_total'] for item in cart_items)
    cur.close()
    con.close()

    return render_template('cart.html', cart_items=cart_items, total=total)


if __name__ == '__main__':
    app.run(debug=True)