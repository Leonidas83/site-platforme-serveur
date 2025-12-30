%%writefile app.py
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, g
import bcrypt # Import bcrypt for password hashing

app = Flask(__name__)
app.config['DATABASE'] = 'extended_database.db'

# --- Database Connection Management ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row # This makes rows behave like dicts
        db.execute("PRAGMA foreign_keys = ON;")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Utility Functions ---

def hash_password(password):
    # Hash a password for storing in the database.
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8') # Store as UTF-8 string

def verify_password(hashed_password, provided_password):
    # Verify a plain-text password against a hashed password.
    return bcrypt.checkpw(provided_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- User Management Functions (Interacting with 'users' table) ---

def add_user(email, password, first_name, last_name):
    conn = get_db()
    cursor = conn.cursor())
    try:
        hashed_pass = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?);",
            (email, hashed_pass, first_name, last_name)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Handles UNIQUE constraint violation for email
        return None # User with this email already exists
    except sqlite3.Error as e:
        print(f"Database error adding user: {e}")
        return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, first_name, last_name FROM users WHERE id = ?;", (user_id,))
    return cursor.fetchone()

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password, first_name, last_name FROM users WHERE email = ?;", (email,))
    return cursor.fetchone()

def search_users(email=None, first_name=None, last_name=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, email, first_name, last_name FROM users WHERE 1=1"
    params = []

    if email:
        query += " AND email LIKE ?"
        params.append(f'%{email}%')
    if first_name:
        query += " AND first_name LIKE ?"
        params.append(f'%{first_name}%')
    if last_name:
        query += " AND last_name LIKE ?"
        params.append(f'%{last_name}%')

    cursor.execute(query, params)
    return cursor.fetchall()

def update_user(user_id, email=None, first_name=None, last_name=None, new_password=None):
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    params = []

    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if first_name is not None:
        updates.append("first_name = ?")
        params.append(first_name)
    if last_name is not None:
        updates.append("last_name = ?")
        params.append(last_name)
    if new_password is not None:
        hashed_pass = hash_password(new_password)
        updates.append("password = ?")
        params.append(hashed_pass)

    if not updates:
        return False # Nothing to update

    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?;"
    params.append(user_id)

    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was updated
    except sqlite3.IntegrityError:
        # Handles UNIQUE constraint violation for email during update
        return False
    except sqlite3.Error as e:
        print(f"Database error updating user: {e}")
        return False

def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was deleted
    except sqlite3.Error as e:
        print(f"Database error deleting user: {e}")
        return False

# --- Service Management Functions (Interacting with 'services' table) ---

def get_all_services():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM services;")
    return cursor.fetchall()

def get_service_by_id(service_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM services WHERE id = ?;", (service_id,))
    return cursor.fetchone()

# --- User Subscription Management Functions (Interacting with 'user_services' table) ---

def get_user_subscriptions(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            us.id AS subscription_id,
            s.id AS service_id,
            s.name AS service_name,
            s.description AS service_description,
            us.active,
            us.start_date,
            us.end_date
        FROM user_services us
        JOIN services s ON us.service_id = s.id
        WHERE us.user_id = ?;
    ''', (user_id,))
    return cursor.fetchall()

def get_user_service_subscription(user_id, service_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            us.id AS subscription_id,
            s.name AS service_name,
            s.description AS service_description,
            us.active,
            us.start_date,
            us.end_date
        FROM user_services us
        JOIN services s ON us.service_id = s.id
        WHERE us.user_id = ? AND us.service_id = ?;
    ''', (user_id, service_id))
    return cursor.fetchone()

def add_user_subscription(user_id, service_id, start_date, end_date=None, active=1):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_services (user_id, service_id, active, start_date, end_date) VALUES (?, ?, ?, ?, ?);",
            (user_id, service_id, active, start_date, end_date)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # This handles the UNIQUE(user_id, service_id) constraint violation
        return None # User already subscribed to this service
    except sqlite3.Error as e:
        print(f"Database error adding subscription: {e}")
        return None

def update_user_subscription(user_id, service_id, active=None, end_date=None):
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    params = []

    if active is not None:
        updates.append("active = ?")
        params.append(active)
    if end_date is not None:
        updates.append("end_date = ?")
        params.append(end_date)

    if not updates:
        return False # Nothing to update

    query = f"UPDATE user_services SET {', '.join(updates)} WHERE user_id = ? AND service_id = ?;"
    params.extend([user_id, service_id])

    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was updated
    except sqlite3.Error as e:
        print(f"Database error updating subscription: {e}")
        return False

def delete_user_subscription(user_id, service_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_services WHERE user_id = ? AND service_id = ?;", (user_id, service_id))
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was deleted
    except sqlite3.Error as e:
        print(f"Database error deleting subscription: {e}")
        return False

# --- API Routes ---

@app.route('/')
def index():
    return "Welcome to the Extended Flask App!"

# --- User API Routes ---

@app.route('/users', methods=['POST'])
def api_add_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not all([email, password, first_name, last_name]):
        return jsonify({'message': 'Missing data'}), 400

    user_id = add_user(email, password, first_name, last_name)
    if user_id:
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
    return jsonify({'message': 'User with this email already exists or another error occurred'}), 409 # Conflict or other error

@app.route('/users', methods=['GET'])
def api_get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, first_name, last_name FROM users;")
    users = cursor.fetchall()
    return jsonify([dict(u) for u in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(dict(user))
    return jsonify({'message': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    data = request.get_json()
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    new_password = data.get('password')

    if not any([email, first_name, last_name, new_password]):
        return jsonify({'message': 'No update data provided'}), 400

    if update_user(user_id, email=email, first_name=first_name, last_name=last_name, new_password=new_password):
        return jsonify({'message': 'User updated successfully'}), 200
    
    # Check if user exists before determining error type
    if not get_user_by_id(user_id):
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'message': 'Failed to update user, possibly duplicate email or no changes made'}), 400

@app.route('/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if delete_user(user_id):
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Email and password are required'}), 400

    user = get_user_by_email(email)
    if user and verify_password(user['password'], password):
        return jsonify({'message': 'Login successful', 'user_id': user['id'], 'email': user['email']}), 200
    return jsonify({'message': 'Invalid credentials'}), 401 # Unauthorized

@app.route('/search/users', methods=['GET'])
def api_search_users():
    email_query = request.args.get('email')
    first_name_query = request.args.get('first_name')
    last_name_query = request.args.get('last_name')

    if not any([email_query, first_name_query, last_name_query]):
        return jsonify({'message': 'Please provide at least one search parameter (email, first_name, or last_name)'}), 400

    users = search_users(email=email_query, first_name=first_name_query, last_name=last_name_query)

    if users:
        return jsonify([dict(u) for u in users])
    return jsonify({'message': 'No users found matching the criteria'}), 404

# --- Service API Routes ---

@app.route('/services', methods=['GET'])
def api_get_services():
    services = get_all_services()
    return jsonify([dict(s) for s in services])

@app.route('/services/<int:service_id>', methods=['GET'])
def api_get_service(service_id):
    service = get_service_by_id(service_id)
    if service:
        return jsonify(dict(service))
    return jsonify({'message': 'Service not found'}), 404

# --- User Subscription API Routes ---

@app.route('/users/<int:user_id>/subscriptions', methods=['GET'])
def api_get_user_subs(user_id):
    subscriptions = get_user_subscriptions(user_id)
    if subscriptions:
        return jsonify([dict(sub) for sub in subscriptions])
    return jsonify({'message': 'No subscriptions found for this user'}), 404

@app.route('/users/<int:user_id>/subscriptions/<int:service_id>', methods=['GET'])
def api_get_user_service_sub(user_id, service_id):
    subscription = get_user_service_subscription(user_id, service_id)
    if subscription:
        return jsonify(dict(subscription))
    return jsonify({'message': 'Subscription not found'}), 404

@app.route('/users/<int:user_id>/subscriptions', methods=['POST'])
def api_add_user_subscription(user_id):
    data = request.get_json()
    service_id = data.get('service_id')
    start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = data.get('end_date')
    active = data.get('active', 1)

    if not service_id:
        return jsonify({'message': 'Service ID is required'}), 400

    # Check if service exists
    if not get_service_by_id(service_id):
        return jsonify({'message': 'Service not found'}), 404

    # Check if user exists
    if not get_user_by_id(user_id):
        return jsonify({'message': 'User not found'}), 404

    sub_id = add_user_subscription(user_id, service_id, start_date, end_date, active)
    if sub_id is not None:
        return jsonify({'message': 'Subscription added successfully', 'subscription_id': sub_id}), 201
    elif sub_id is None:
         return jsonify({'message': 'User is already subscribed to this service'}), 409 # Conflict
    return jsonify({'message': 'Failed to add subscription'}), 500

@app.route('/users/<int:user_id>/subscriptions/<int:service_id>', methods=['PUT'])
def api_update_user_subscription(user_id, service_id):
    data = request.get_json()
    active = data.get('active')
    end_date = data.get('end_date')

    # Check if user and service exist
    if not get_user_by_id(user_id):
        return jsonify({'message': 'User not found'}), 404
    if not get_service_by_id(service_id):
        return jsonify({'message': 'Service not found'}), 404

    # Convert active to int if provided
    if active is not None:
        try:
            active = int(active)
        except ValueError:
            return jsonify({'message': 'Active status must be 0 or 1'}), 400

    if update_user_subscription(user_id, service_id, active=active, end_date=end_date):
        return jsonify({'message': 'Subscription updated successfully'}), 200
    return jsonify({'message': 'Subscription not found or nothing to update'}), 404

@app.route('/users/<int:user_id>/subscriptions/<int:service_id>', methods=['DELETE'])
def api_delete_user_subscription(user_id, service_id):
    # Check if user and service exist
    if not get_user_by_id(user_id):
        return jsonify({'message': 'User not found'}), 404
    if not get_service_by_id(service_id):
        return jsonify({'message': 'Service not found'}), 404

    if delete_user_subscription(user_id, service_id):
        return jsonify({'message': 'Subscription deleted successfully'}), 200
    return jsonify({'message': 'Subscription not found'}), 404

# To run this Flask app:
# 1. Save this code as `app.py`
# 2. Make sure `extended_database.db` is initialized with data (from the previous step `initialize_database.py`).
# 3. Run: `flask run` in your terminal
# (You might need to set FLASK_APP=app.py and FLASK_ENV=development first)

# Example of how to run the app directly from a script (for testing/colab context)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
