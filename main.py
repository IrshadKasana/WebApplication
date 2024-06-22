from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from cryptography.fernet import Fernet
import random
import string

app = Flask(__name__)

# Initialize or load your encryption key securely. Here, we generate a key.
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# SQLite database file path
db_file = 'data.db'

# Function to encrypt UID
def encrypt_uid(uid):
    encrypted_id = cipher_suite.encrypt(uid.encode()).decode()
    return encrypted_id

# Function to create SQLite databases and tables
def create_database():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create maintable
    c.execute('''CREATE TABLE IF NOT EXISTS maintable (
                 uid TEXT PRIMARY KEY,
                 username TEXT UNIQUE,
                 status TEXT,
                 business_ac INTEGER,
                 encrypted_uid TEXT
                 )''')

    # Create company table
    c.execute('''CREATE TABLE IF NOT EXISTS company (
                 username TEXT,
                 encrypted_uid TEXT,
                 status TEXT
                 )''')

    conn.commit()
    conn.close()

    # Prefill maintable with dummy data
    prefill_maintable()

def prefill_maintable():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    for i in range(1000):
        uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        username = f'user{i}'
        status = 'F' if i % 2 == 0 else 'T'
        business_ac = random.randint(100000, 999999)
        encrypted_uid = encrypt_uid(uid)

        try:
            c.execute("INSERT INTO maintable (uid, username, status, business_ac, encrypted_uid) VALUES (?, ?, ?, ?, ?)",
                      (uid, username, status, business_ac, encrypted_uid))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

# Function to insert a user into maintable
def insert_user(uid, status, username, business_ac):
    encrypted_id = encrypt_uid(uid)

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO maintable (uid, status, username, business_ac, encrypted_uid) VALUES (?, ?, ?, ?, ?)",
                  (uid, status, username, business_ac, encrypted_id))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists. User not added.")

    conn.close()

# Function to retrieve all users from maintable
def retrieve_users():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("SELECT * FROM maintable")
    users = c.fetchall()

    conn.close()
    return users

# Function to retrieve all users from company
def retrieve_company_users():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("SELECT * FROM company")
    users = c.fetchall()

    conn.close()
    return users

# Route for profile page
@app.route('/')
def profile():
    return render_template('profile.html')

# Route for verify page
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        uid = request.form['uid']
        otp = request.form['otp']  # Assuming OTP is not actually used

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM maintable WHERE uid=?", (uid,))
        user = c.fetchone()

        if not user:
            return redirect(url_for('outpa'))

        uid, username, status, business_ac, encrypted_uid = user

        if status == 'T':
            return redirect(url_for('outpa'))
        else:
            # Update status to 'T' and add to company table
            c.execute("UPDATE maintable SET status='T' WHERE uid=?", (uid,))
            c.execute("INSERT INTO company (username, encrypted_uid, status) VALUES (?, ?, ?)",
                      (username, encrypted_uid, 'T'))
            conn.commit()
            conn.close()
            return redirect(url_for('success'))

    return render_template('verify.html')

# Route for add_user page
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        uid = request.form['uid']
        status = request.form['status']
        username = request.form['username']
        business_ac = request.form['business_ac']

        insert_user(uid, status, username, business_ac)
        return redirect(url_for('view_users'))

    return render_template('add_user.html')

# Route for viewing all users in maintable
@app.route('/view_users')
def view_users():
    users = retrieve_users()
    return render_template('view_users.html', users=users)

# Route for viewing all users in company table
@app.route('/view_company_users')
def view_company_users():
    users = retrieve_company_users()
    return render_template('view_company_users.html', users=users)

# Route for outpa page
@app.route('/outpa')
def outpa():
    return render_template('outpa.html')

# Route for success page
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    create_database()  # Ensure databases and tables are created when running the application
    app.run(host='0.0.0.0', port=5000, debug=True)
