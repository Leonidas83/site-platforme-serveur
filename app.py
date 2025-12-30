import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, g

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

# --- Example API Routes ---

@app.route('/')
def index():
    return "Welcome to the Extended Flask App!"

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

    # Check if user exists (assuming users table exists and is populated)
    # For a full app, you'd check `users` table, but for this context, just relying on foreign key

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
    if delete_user_subscription(user_id, service_id):
        return jsonify({'message': 'Subscription deleted successfully'}), 200
    return jsonify({'message': 'Subscription not found'}), 404


# To run this Flask app:
# 1. Save this code as `app.py`
# 2. Make sure `extended_database.db` is initialized with data (from the previous step).
# 3. Run: `flask run` in your terminal
# (You might need to set FLASK_APP=app.py and FLASK_ENV=development first)

# Example of how to run the app directly from a script (for testing/colab context)
# if __name__ == '__main__':
#     app.run(debug=True)
