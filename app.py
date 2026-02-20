from flask import Flask, request, jsonify
from flasgger import Swagger
import json
import re
import os
import uuid

app = Flask(__name__)

# ==============================
# Swagger Configuration (JWT Style)
# ==============================
app.config['SWAGGER'] = {
    "title": "Fitness Booking API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Fitness Booking API",
        "description": "API with Token-Based Authentication",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: Bearer <your_token>"
        }
    }
}

swagger = Swagger(app, template=swagger_template)

# ==============================
# Helper Functions
# ==============================

def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize databases
users_db = load_json("users_db.json")
classes_db = load_json("classes_db.json")
active_tokens = {}

def save_classes():
    with open('classes_db.json', 'w') as file:
        json.dump(classes_db, file, indent=4)

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password)
    )

def authenticate_token():
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None

    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    return active_tokens.get(token)

# ==============================
# Register
# ==============================
@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
            - phone
            - role
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
            phone:
              type: string
            role:
              type: string
              enum: [Member, Trainer, Admin]
    responses:
      201:
        description: User registered
    """

    data = request.get_json()

    required = ['name', 'email', 'password', 'phone', 'role']
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if not is_strong_password(data['password']):
        return jsonify({"error": "Password must be 8+ chars, include uppercase, lowercase, number"}), 400

    if data['role'] not in ['Member', 'Trainer', 'Admin']:
        return jsonify({"error": "Invalid role"}), 400

    if any(user['email'] == data['email'] for user in users_db):
        return jsonify({"error": "Email already registered"}), 400

    users_db.append(data)
    save_json("users_db.json", users_db)

    return jsonify({"message": "User registered successfully"}), 201


# ==============================
# Login (Generates Token)
# ==============================
@app.route('/login', methods=['POST'])
def login():
    """
    Login and receive authentication token
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Returns authentication token
    """

    data = request.get_json()

    user = next(
        (u for u in users_db if u['email'] == data.get('email') and u['password'] == data.get('password')),
        None
    )

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = str(uuid.uuid4())
    active_tokens[token] = user

    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200


# ==============================
# Create Class (Admin/Trainer)
# ==============================
@app.route('/classes', methods=['POST'])
def create_class():
    """
    Create a fitness class
    ---
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - venue
            - capacity
            - date
            - start_time
            - end_time
          properties:
            title:
              type: string
              example: Yoga
            venue:
              type: string
              example: Room A
            capacity:
              type: integer
              example: 20
            date:
              type: string
              example: 2026-03-20
            start_time:
              type: string
              example: 10:00
            end_time:
              type: string
              example: 11:00
    responses:
      201:
        description: Class created successfully
      403:
        description: Unauthorized
    """

    user = authenticate_token()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403

    if user['role'] not in ['Admin', 'Trainer']:
        return jsonify({"error": "Only Admin or Trainer can create classes"}), 403

    data = request.get_json()

    required_fields = ['title', 'venue', 'capacity', 'date', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        capacity = int(data['capacity'])
        if capacity <= 0:
            return jsonify({"error": "Capacity must be > 0"}), 400
    except:
        return jsonify({"error": "Capacity must be number"}), 400

    new_class = {
        "id": max([c.get('id', 0) for c in classes_db], default=0) + 1,
        "title": data['title'],
        "venue": data['venue'],
        "capacity": capacity,
        "date": data['date'],
        "start_time": data['start_time'],
        "end_time": data['end_time'],
        "created_by": user['email'],
        "booked_members": []
    }

    classes_db.append(new_class)
    save_classes()

    return jsonify({"message": "Class created", "class": new_class}), 201


# ==============================
# View Classes (Admin/Trainer only)
# ==============================
@app.route('/classes', methods=['GET'])
def view_classes():
    """
    View all classes
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: List of classes
        schema:
          type: object
          properties:
            classes:
              type: array
              items:
                type: object
    """

    user = authenticate_token()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403

    if user['role'] not in ['Admin', 'Trainer']:
        return jsonify({"error": "Only Admin/Trainer can view classes"}), 403

    if not classes_db:
        return jsonify({"message": "No classes available"}), 200

    return jsonify({"classes": classes_db}), 200


# ==============================
# Book Class (Member Only)
# ==============================
@app.route('/classes/<int:class_id>/book', methods=['POST'])
def book_class(class_id):
    """
    Book a class
    ---
    security:
      - Bearer: []
    parameters:
      - name: class_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Booking successful
      403:
        description: Unauthorized
      404:
        description: Class not found
    """

    user = authenticate_token()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403

    if user['role'] != 'Member':
        return jsonify({"error": "Only Members can book"}), 403

    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found"}), 404

    if user['email'] in fitness_class['booked_members']:
        return jsonify({"error": "Already booked"}), 400

    if len(fitness_class['booked_members']) >= fitness_class['capacity']:
        return jsonify({"error": "Class full"}), 400

    fitness_class['booked_members'].append(user['email'])
    save_classes()

    return jsonify({"message": "Booking successful"}), 200


# ==============================
# View Members (Admin/Trainer)
# ==============================
@app.route('/classes/<int:class_id>/members', methods=['GET'])
def view_members(class_id):
    """
    View members of a class
    ---
    security:
      - Bearer: []
    parameters:
      - name: class_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: List of members
      403:
        description: Unauthorized
      404:
        description: Class not found
    """
    
    user = authenticate_token()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403

    if user['role'] not in ['Admin', 'Trainer']:
        return jsonify({"error": "Only Admin/Trainer allowed"}), 403

    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found"}), 404

    return jsonify({
        "class_id": class_id,
        "booked_members": fitness_class['booked_members']
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)