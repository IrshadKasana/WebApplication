import sqlite3
import random
import string
from cryptography.fernet import Fernet

# Initialize or load your encryption key securely. Here, we generate a key.
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# SQLite database file path
db_file = 'adhar.db'

# Create SQLite database and table
def create_database():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 uid TEXT PRIMARY KEY,
                 status TEXT,
                 username TEXT UNIQUE,
                 business_ac TEXT,
                 encrypted_uid TEXT
                 )''')

    conn.commit()
    conn.close()

# Function to encrypt UID
def encrypt_uid(uid):
    encrypted_id = cipher_suite.encrypt(uid.encode()).decode()
    return encrypted_id

# Function to decrypt UID (just for demonstration, not needed in this example)
def decrypt_uid(encrypted_uid):
    decrypted_id = cipher_suite.decrypt(encrypted_uid.encode()).decode()
    return decrypted_id

# Function to generate dummy data and insert users into the database
def insert_dummy_data(num_users=100):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    for _ in range(num_users):
        uid = f"EU80057501{''.join(random.choices(string.digits, k=5))}"  # Generate UID starting with EU80057501
        status = random.choice(['True', 'False'])  # Random status
        username = ''.join(random.choices(string.ascii_lowercase, k=8))  # Random username (8 characters)
        business_ac = ''.join(random.choices(string.ascii_uppercase, k=5))  # Random business account (5 characters)
        encrypted_id = encrypt_uid(uid)  # Encrypt UID

        try:
            c.execute("INSERT INTO users (uid, status, username, business_ac, encrypted_uid) VALUES (?, ?, ?, ?, ?)",
                      (uid, status, username, business_ac, encrypted_id))
        except sqlite3.IntegrityError:
            print(f"Username '{username}' already exists. Skipping.")

    conn.commit()
    conn.close()
    print(f"{num_users} users inserted successfully.")

# Function to retrieve all users from the database (for testing purposes)
def retrieve_users():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    users = c.fetchall()

    conn.close()
    return users

# Uncomment the following line to create the database and table if they don't exist
# create_database()

# Example usage to insert dummy data (comment out after running once)
# insert_dummy_data()

# Example usage to retrieve users (for testing purposes)
# users = retrieve_users()
# print(users)
