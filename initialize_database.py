```python
# initialize_database.py

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

# Optional: Verify data (for demonstration purposes, not part of the final script)
# def verify_data():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     print("\n--- Verifying Data ---")
#     cursor.execute("SELECT * FROM users;")
#     print("Users:", cursor.fetchall())
#     cursor.execute("SELECT * FROM services;")
#     print("Services:", cursor.fetchall())
#     cursor.execute("SELECT * FROM user_services;")
#     print("User Services:", cursor.fetchall())
#     conn.close()

# if __name__ == '__main__':
#     verify_data()
```

The above code snippet represents the complete content of the `initialize_database.py` file. This script, when executed, will create the `extended_database.db` SQLite file with the `users`, `services`, and `user_services` tables, and populate them with initial data including securely hashed passwords. This completes the subtask of generating the `initialize_database.py` file with all specified functionalities.

Now, to confirm the subtask is done, I'll use the `finish_task` command.

```markdown
**Instructions for the user:**

1.  Save the code block above as `initialize_database.py` in your project directory.
2.  Run the script from your terminal: `python initialize_database.py`
3.  This will create the `extended_database.db` file with the schema and initial data.
```

Explanation:

1.  **Libraries:** The code imports `sqlite3`, `datetime`, and `bcrypt`. `bcrypt` is used for securely hashing passwords.
2.  **Database Connection and Foreign Keys:** The `initialize_db` function establishes a connection to the `extended_database.db` and ensures foreign key support is enabled using `PRAGMA foreign_keys = ON;`. This is crucial for maintaining relational integrity.
3.  **`create_tables` Function:** This function contains the `CREATE TABLE IF NOT EXISTS` statements for `users`, `services`, and `user_services`, matching the schema defined in the previous steps. `IF NOT EXISTS` prevents errors if the script is run multiple times and tables already exist.
4.  **`hash_password` Function:** This utility function takes a plain-text password, hashes it using `bcrypt.gensalt()` and `bcrypt.hashpw()`, and returns the hashed string. This is a best practice for storing passwords securely.
5.  **`insert_initial_data` Function:**
    *   It first checks if data already exists in each table (`SELECT COUNT(*)`) before attempting to insert new data. This prevents duplicate entries if the script is run multiple times.
    *   **Users:** Inserts sample user data. For each user, the plain-text password is passed to `hash_password()` before insertion.
    *   **Services:** Inserts sample service data.
    *   **User Services (Subscriptions):** Inserts sample subscription data. It dynamically fetches `user_id` and `service_id` from the newly inserted users and services to establish correct foreign key relationships. It includes examples of active, inactive, and ongoing subscriptions with start and end dates.
6.  **`initialize_db` Function Orchestration:** This function calls `create_tables()` and `insert_initial_data()` in sequence. It also includes `conn.commit()` to save changes and `conn.close()` to properly close the database connection.
7.  **Main Block (`if __name__ == '__main__':`):** This block ensures that `initialize_db()` is called only when the script is executed directly (not when imported as a module). Print statements are added to provide feedback on the script's progress.

This script is self-contained and fulfills all requirements of the subtask for setting up the extended database schema and populating it with initial, securely handled data.

