from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

@app.route('/addStudent', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    mark = data.get('mark')
    cursor = db.cursor()
    sql_query = "INSERT INTO students (name, mark) VALUES (%s, %s)"
    cursor.execute(sql_query, (name, mark))
    db.commit()  # this saves the value permanently in our table
    return jsonify({'message': 'Student added successfully'}), 201

@app.route('/update', methods=['PUT'])
def update_data():
    id = request.json.get('id')
    name = request.json.get('name')
    mark = request.json.get('mark')
    cursor = db.cursor()
    query = "UPDATE students SET name = %s, mark = %s WHERE id = %s"
    cursor.execute(query, (name, mark, id))
    db.commit()
    cursor.close()
    return jsonify({'message': 'Student updated successfully'}), 200

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_data(id):
    cursor = db.cursor()
    query = "DELETE FROM students WHERE id = %s"
    cursor.execute(query, (id,))
    db.commit()
    cursor.close()
    return jsonify({'message': 'Student deleted successfully'}), 200

@app.route('/fetchAll', methods=['GET'])
def fetch_all():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)


@app.route('/fetchById/<int:id>', methods=['GET'])  
def fetch_by_id(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s" , (id,))
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route('/postList', methods=['POST'])
def post_list():
    reqData = request.get_json()
    cursor = db.cursor()
    query = "INSERT INTO students (name, mark) VALUES (%s, %s)"
    for student in reqData:
        name = student.get('name')
        mark = student.get('mark')
        cursor.execute(query, (name, mark))
    db.commit()
    cursor.close()
    return jsonify({'message': 'list posted'}), 201

if __name__ == '__main__':
    print("connecting to database....")
    app.run() 