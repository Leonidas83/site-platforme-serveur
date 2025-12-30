%%writefile initialize_database.py
import sqlite3
from datetime import datetime, timedelta
import bcrypt

DB_NAME = 'extended_database.db'

def hash_password(password):
    # Hash a password for storing in the database.
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8') # Store as UTF-8 string

def create_tables(cursor):
    # 1. Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL
        );
    ''')
    print("Table 'users' created or already exists.")

    # 2. Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );
    ''')
    print("Table 'services' created or already exists.")

    # 3. Create user_services liaison table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            start_date TEXT NOT NULL,
            end_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
            UNIQUE(user_id, service_id)
        );
    ''')
    print("Table 'user_services' created or already exists.")

def insert_initial_data(cursor):
    # Check if users exist to prevent re-insertion
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        print("Inserting initial user data...")
        users_data = [
            ('alice@example.com', 'Alice', 'Smith', 'password123'),
            ('bob@example.com', 'Bob', 'Johnson', 'securepass'),
            ('charlie@example.com', 'Charlie', 'Brown', 'qwerty')
        ]
        for email, first_name, last_name, raw_password in users_data:
            hashed_pass = hash_password(raw_password)
            cursor.execute(
                "INSERT INTO users (email, first_name, last_name, password) VALUES (?, ?, ?, ?)",
                (email, first_name, last_name, hashed_pass)
            )
        print("Initial user data inserted.")

    # Check if services exist
    cursor.execute("SELECT COUNT(*) FROM services;")
    if cursor.fetchone()[0] == 0:
        print("Inserting initial service data...")
        services_data = [
            ('Premium Support', '24/7 priority support for critical issues.'),
            ('Advanced Analytics', 'Access to in-depth data analysis tools.'),
            ('Cloud Storage Pro', '1TB secure cloud storage with advanced features.')
        ]
        cursor.executemany(
            "INSERT INTO services (name, description) VALUES (?, ?)",
            services_data
        )
        print("Initial service data inserted.")

    # Check if user_services exist
    cursor.execute("SELECT COUNT(*) FROM user_services;")
    if cursor.fetchone()[0] == 0:
        print("Inserting initial user_services data...")
        # Fetch user and service IDs for linking
        cursor.execute("SELECT id, email FROM users;")
        users = {email: uid for uid, email in cursor.fetchall()}
        cursor.execute("SELECT id, name FROM services;")
        services = {name: sid for sid, name in cursor.fetchall()}

        today = datetime.now()
        next_month = today + timedelta(days=30)
        next_year = today + timedelta(days=365)

        user_services_data = [
            (users['alice@example.com'], services['Premium Support'], 1, today.strftime('%Y-%m-%d'), next_year.strftime('%Y-%m-%d')),
            (users['alice@example.com'], services['Cloud Storage Pro'], 1, today.strftime('%Y-%m-%d'), None), # No end date
            (users['bob@example.com'], services['Advanced Analytics'], 1, today.strftime('%Y-%m-%d'), next_month.strftime('%Y-%m-%d')),
            (users['charlie@example.com'], services['Premium Support'], 0, (today - timedelta(days=60)).strftime('%Y-%m-%d'), (today - timedelta(days=30)).strftime('%Y-%m-%d')) # Inactive/expired
        ]
        cursor.executemany(
            "INSERT INTO user_services (user_id, service_id, active, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            user_services_data
        )
        print("Initial user_services data inserted.")

def initialize_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")

        create_tables(cursor)
        insert_initial_data(cursor)

        conn.commit()
        print(f"Database '{DB_NAME}' schema and initial data successfully set up.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Attempting to initialize the extended database...")
    initialize_db()
    print("Initialization complete.")
