from flask import Flask, request, jsonify
from flasgger import Swagger
import json

app = Flask(__name__)
swagger = Swagger(app)

classes_db = []

# Load existing classes from file
try:
    with open('classes_db.json', 'r') as file:
        classes_db = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    classes_db = []


# ===============================
# Feature 1: Create Class
# ===============================
@app.route('/classes', methods=['POST'])
def create_class():
    """
    Create a fitness class
    ---
    parameters:
      - name: Role
        in: header
        type: string
        required: true
        description: Must be Admin or Trainer
      - name: body
        in: body
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
            venue:
              type: string
            capacity:
              type: integer
            date:
              type: string
            start_time:
              type: string
            end_time:
              type: string
    responses:
      201:
        description: Class created successfully
      400:
        description: Invalid input
      403:
        description: Unauthorized
    """

    user_role = request.headers.get('Role')

    if user_role not in ['Admin', 'Trainer']:
        return jsonify({"error": "Unauthorized: Only Admins or Trainers can create classes."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ['title', 'venue', 'capacity', 'date', 'start_time', 'end_time']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        capacity = int(data['capacity'])
        if capacity <= 0:
            return jsonify({"error": "Capacity must be greater than 0"}), 400
    except ValueError:
        return jsonify({"error": "Capacity must be a number"}), 400

    new_class = {
        "id": max([c['id'] for c in classes_db], default=0) + 1,
        "title": data['title'],
        "venue": data['venue'],
        "capacity": capacity,
        "date": data['date'],
        "start_time": data['start_time'],
        "end_time": data['end_time'],
        "created_by": user_role,
        "booked_members": []
    }

    classes_db.append(new_class)

    with open('classes_db.json', 'w') as file:
        json.dump(classes_db, file)

    return jsonify({"message": "Class created successfully", "class": new_class}), 201


# ===============================
# Feature 2: View Classes
# ===============================
@app.route('/classes', methods=['GET'])
def view_classes():
    """
    View all fitness classes
    ---
    responses:
      200:
        description: Returns list of classes or message if empty
    """

    if not classes_db:
        return jsonify({"message": "No classes available"}), 200

    return jsonify({"classes": classes_db}), 200


# ===============================
# Feature 3: Book a Class
# ===============================
@app.route('/classes/<int:class_id>/book', methods=['POST'])
def book_class(class_id):
    """
    Book a fitness class
    ---
    parameters:
      - name: class_id
        in: path
        type: integer
        required: true
      - name: Role
        in: header
        type: string
        required: true
        description: Must be Member
      - name: User
        in: header
        type: string
        required: true
        description: Member name
    responses:
      200:
        description: Booking successful
      400:
        description: Class full or already booked
      403:
        description: Unauthorized
      404:
        description: Class not found
    """

    user_role = request.headers.get('Role')
    member_name = request.headers.get('User')

    if user_role != 'Member':
        return jsonify({"error": "Unauthorized: Only Members can book classes."}), 403

    if not member_name:
        return jsonify({"error": "Member name is required in header."}), 400

    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found."}), 404

    if member_name in fitness_class['booked_members']:
        return jsonify({"error": "Member already booked this class."}), 400

    if len(fitness_class['booked_members']) >= fitness_class['capacity']:
        return jsonify({"error": "Class is full."}), 400

    fitness_class['booked_members'].append(member_name)

    with open('classes_db.json', 'w') as file:
        json.dump(classes_db, file)

    return jsonify({"message": "Booking successful."}), 200


# ===============================
# Feature 4: View Member List
# ===============================
@app.route('/classes/<int:class_id>/members', methods=['GET'])
def view_members(class_id):
    """
    View members of a class
    ---
    parameters:
      - name: class_id
        in: path
        type: integer
        required: true
      - name: Role
        in: header
        type: string
        required: true
        description: Must be Admin or Trainer
    responses:
      200:
        description: List of booked members
      403:
        description: Unauthorized
      404:
        description: Class not found
    """

    user_role = request.headers.get('Role')

    if user_role not in ['Admin', 'Trainer']:
        return jsonify({"error": "Unauthorized: Only Admins or Trainers can view member list."}), 403

    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found."}), 404

    if not fitness_class.get('booked_members'):
        return jsonify({"message": "No members have booked this class yet."}), 200

    return jsonify({
        "class_id": class_id,
        "booked_members": fitness_class['booked_members']
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)