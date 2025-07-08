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