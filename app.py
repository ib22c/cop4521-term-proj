from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import *
import psycopg2.extras
from auth import *
from functools import wraps


app = Flask(__name__)
app.secret_key = 'wubahubalub3456765' #no one guessing ts


"""In check_user_permission() in database.py, I assigned each role to a number
Customer = 1, Vendor = 2, Employee = 3, Admin = 4
The require_role() decorator checks this
if a page requires Vendor to access it, Employee and Admin can also access it
If a page requires Employee, only Employee and Admin can see it, not Vendor or Customer"""

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_auth():
                return redirect(url_for('login'))
            
            user_id = session.get('user_id')
            if not user_id:
                flash('Please log in')
                return redirect(url_for('login'))
            
            if not check_user_permission(user_id, required_role):
                user_role = get_user_role(user_id)
                flash(f'ACCESS DENIED! Required role: {required_role}')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user_role():
    if not check_auth():
        return None
    return get_user_role(session.get('user_id'))

def check_auth():
    return 'user_id' in session

def require_auth():
    if not check_auth():
        return redirect(url_for('login'))
    return None

def general_auth():
    auth_redirect = require_auth()
    if auth_redirect:
        return auth_redirect

@app.route('/')
def decision():
    if check_auth():
        user_role = get_current_user_role()
        if user_role == 'Vendor':
            return redirect(url_for('vendor_dashboard'))
        elif user_role == 'Employee':
            return redirect(url_for('employee_dashboard'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('signup_selection'))

@app.route('/signup_selection')
def signup_selection():
    return render_template('signup_selection.html')

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


#making sure only vendors can sign up as vendors is tricky, we have two options:
#make a secret vendor code (which is what this does)
#make a portal for admin/employee that has to approve vendors (i think this is doing too much)

@app.route('/signup/vendor', methods=['GET', 'POST'])
def vendor_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        vendor_code = request.form.get('vendor_code') 

        if not all([email, first_name, last_name, password, vendor_code]):
            flash('All fields are required')
            return render_template('vendor_signup.html')
        
        if vendor_code != "12345": #we can change this
            flash('Imposter! You are not a vendor!')
            return render_template('vendor_signup.html')
        
        user_id, message = create_user(email, first_name, last_name, password, role='Vendor')

        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['first_name'] = first_name
            flash('Vendor successfully created!')
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(message, 'error')
            return render_template('vendor_signup.html')
        
    return render_template('vendor_signup.html')


#same options here, to start i will go with the secret code
@app.route('/signup/employee', methods=['GET', 'POST'])
def employee_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        employee_code = request.form.get('employee_code') 

        if not all([email, first_name, last_name, password, employee_code]):
            flash('All fields are required')
            return render_template('employee_signup.html')
        
        if employee_code != "12345": #again, we can change this
            flash('Imposter! You are not an employee!')
            return render_template('employee_signup.html')
        
        user_id, message = create_user(email, first_name, last_name, password, role='Employee')

        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['first_name'] = first_name
            flash('Employee successfully created!')
            return redirect(url_for('employee_dashboard'))
        else:
            flash(message, 'error')
            return render_template('employee_signup.html')
        
    return render_template('employee_signup.html')

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


            user_role = get_user_role(user['user_id'])
            if user_role == 'Vendor':
                return redirect(url_for('vendor_dashboard'))
            elif user_role == 'Employee':
                return redirect(url_for('employee_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('signup_selection'))

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
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        cur.execute("SELECT title FROM Book WHERE book_id = %s", (book_id,))
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


#dashboards:

@app.route('/vendor/dashboard')
@require_role('Vendor')
def vendor_dashboard():
    user_id = session['user_id']
    con = get_db_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT b.book_id, b.title, b.price, b.image_id, a.author_name, c.category_name
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        JOIN Category c ON b.category_id = c.category_id
        WHERE b.uploaded_by = %s
        ORDER BY b.book_id DESC
    """, (user_id,))

    books = cur.fetchall()
    cur.close()
    con.close()

    return render_template('vendor_dashboard.html', books=books)

@app.route('/employee/dashboard')
@require_role('Employee')
def employee_dashboard():
    con = get_db_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT b.book_id, b.title, b.price, b.image_id, a.author_name, c.category_name, 
               u.first_name as uploaded_by_name
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        JOIN Category c ON b.category_id = c.category_id
        LEFT JOIN Users u ON b.uploaded_by = u.user_id
        ORDER BY b.book_id DESC
    """)

    books = cur.fetchall()
    cur.close()
    con.close()

    return render_template('employee_dashboard.html', books=books)



if __name__ == '__main__':
    app.run(debug=True)