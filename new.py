from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Request body is required'
        }), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'error': 'Username and password are required'
        }), 400

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = %s",
        (username,)
    )

    user = cursor.fetchone()
    cursor.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({
            'error': 'Invalid username or password'
        }), 401

    payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm='HS256'
    )

    return jsonify({
        'message': 'Login successful',
        'token': token
    }), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                'error': 'Token is missing'
            }), 401

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=['HS256']
            )

            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token has expired'
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid token'
            }), 401

        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if request.user.get('role') != 'admin':
            return jsonify({
                'error': 'Admin access required'
            }), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/addStudent', methods=['POST'])
@token_required
@admin_required
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    name = data.get('name')
    mark = data.get('mark')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if mark is None:
        return jsonify({'error': 'Mark is required'}), 400

    try:
        mark = float(mark)
    except (ValueError, TypeError):
        return jsonify({'error': 'Mark must be a number'}), 400

    if mark < 0 or mark > 100:
        return jsonify({'error': 'Mark must be between 0 and 100'}), 400

    cursor = db.cursor()

    sql_query = """
        INSERT INTO students (name, mark)
        VALUES (%s, %s)
    """

    cursor.execute(sql_query, (name, mark))
    db.commit()
    cursor.close()

    return jsonify({
        'message': 'Student added successfully'
    }), 201


@app.route('/update', methods=['PUT'])
@token_required
@admin_required
def update_data():
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Request body is required'
        }), 400

    id = data.get('id')
    name = data.get('name')
    mark = data.get('mark')

    if id is None:
        return jsonify({
            'error': 'Student ID is required'
        }), 400

    if not name:
        return jsonify({
            'error': 'Name is required'
        }), 400

    if mark is None:
        return jsonify({
            'error': 'Mark is required'
        }), 400

    try:
        mark = float(mark)
    except (ValueError, TypeError):
        return jsonify({
            'error': 'Mark must be a number'
        }), 400

    if mark < 0 or mark > 100:
        return jsonify({
            'error': 'Mark must be between 0 and 100'
        }), 400

    cursor = db.cursor()

    # Check whether student exists
    cursor.execute(
        "SELECT id FROM students WHERE id = %s",
        (id,)
    )

    student = cursor.fetchone()

    if not student:
        cursor.close()
        return jsonify({
            'error': 'Student not found'
        }), 404

    # Update student
    query = """
        UPDATE students
        SET name = %s, mark = %s
        WHERE id = %s
    """

    cursor.execute(query, (name, mark, id))
    db.commit()
    cursor.close()

    return jsonify({
        'message': 'Student updated successfully'
    }), 200

@app.route('/delete/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_data(id):
    cursor = db.cursor()

    query = "DELETE FROM students WHERE id = %s"

    cursor.execute(query, (id,))

    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({
            'error': 'Student not found'
        }), 404

    db.commit()
    cursor.close()

    return jsonify({
        'message': 'Student deleted successfully'
    }), 200

@app.route('/fetchAll', methods=['GET'])
@token_required
def fetch_all():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)


@app.route('/fetchById/<int:id>', methods=['GET'])
@token_required
def fetch_by_id(id):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students WHERE id = %s",
        (id,)
    )

    student = cursor.fetchone()
    cursor.close()

    if not student:
        return jsonify({
            'error': 'Student not found'
        }), 404

    return jsonify(student), 200

@app.route('/search', methods=['GET'])
@token_required
def search_students():
    name = request.args.get('name')

    if not name:
        return jsonify({
            'error': 'Search name is required'
        }), 400

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT * FROM students
        WHERE name LIKE %s
    """

    cursor.execute(query, (f"%{name}%",))

    students = cursor.fetchall()
    cursor.close()

    if not students:
        return jsonify({
            'message': 'No students found'
        }), 404

    return jsonify(students), 200


@app.route('/postList', methods=['POST'])
@token_required
@admin_required
def post_list():
    req_data = request.get_json()

    if not req_data:
        return jsonify({
            'error': 'Request body is required'
        }), 400

    if not isinstance(req_data, list):
        return jsonify({
            'error': 'Request body must be a list'
        }), 400

    cursor = db.cursor()

    query = """
        INSERT INTO students (name, mark)
        VALUES (%s, %s)
    """

    for student in req_data:
        if not isinstance(student, dict):
            cursor.close()
            return jsonify({
                'error': 'Each student must be an object'
            }), 400

        name = student.get('name')
        mark = student.get('mark')

        if not name:
            cursor.close()
            return jsonify({
                'error': 'Name is required'
            }), 400

        if mark is None:
            cursor.close()
            return jsonify({
                'error': 'Mark is required'
            }), 400

        try:
            mark = float(mark)
        except (ValueError, TypeError):
            cursor.close()
            return jsonify({
                'error': 'Mark must be a number'
            }), 400

        if mark < 0 or mark > 100:
            cursor.close()
            return jsonify({
                'error': 'Mark must be between 0 and 100'
            }), 400

        cursor.execute(query, (name, mark))

    db.commit()
    cursor.close()

    return jsonify({
        'message': 'Students added successfully'
    }), 201

if __name__ == '__main__':
    print("connecting to database....")
    app.run() 