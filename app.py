from flask import Flask, request, jsonify
import json

app = Flask(__name__)

classes_db = []

#load all the classes that were created previously
try:
    with open('classes_db.json', 'r') as file:
        classes_db = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    classes_db = []



@app.route('/classes', methods=['POST'])
def create_class():
    # Requirement: Only Admin or Trainer can create classes.
    user_role = request.headers.get('Role')
    
    if user_role not in ['Admin', 'Trainer']:
        return jsonify({"error": "Unauthorized: Only Admins or Trainers can create classes."}), 403
    
    data = request.get_json()
    required_fields = ['title', 'venue', 'capacity', 'date', 'start_time', 'end_time']
    
    # Check for missing fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Check validity
    try:
        if int(data['capacity']) <= 0:
            return jsonify({"error": "Capacity must be greater than 0"}), 400
    except ValueError:
        return jsonify({"error": "Capacity must be a number"}), 400

    # Create and Save class
    new_class = {
        "id": len(classes_db) + 1,
        "title": data['title'],
        "venue": data['venue'],
        "capacity": int(data['capacity']),
        "date": data['date'],
        "start_time": data['start_time'],
        "end_time": data['end_time'],
        "created_by": user_role,
        "booked_members": []
    }
    
    classes_db.append(new_class)

    # Save classes to a file
    with open('classes_db.json', 'w') as file:
        json.dump(classes_db, file)

    return jsonify({"message": "Class created successfully", "class": new_class}), 201



@app.route('/classes', methods=['GET'])
def view_classes():
    #everyone can view the classes, so no role check is needed
    #get the list of all classes
    if not classes_db:
        return jsonify({"message": "No classes available"}), 200

    return jsonify({"classes": classes_db}), 200


@app.route('/classes/<int:class_id>/book', methods=['POST'])
def book_class(class_id):

    user_role = request.headers.get('Role')
    member_name = request.headers.get('User')

    # Only Member can book
    if user_role != 'Member':
        return jsonify({"error": "Unauthorized: Only Members can book classes."}), 403

    if not member_name:
        return jsonify({"error": "Member name is required in header."}), 400

    # Find class
    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found."}), 404

    # Check duplicate booking
    if member_name in fitness_class['booked_members']:
        return jsonify({"error": "Member already booked this class."}), 400

    # Check capacity
    if len(fitness_class['booked_members']) >= fitness_class['capacity']:
        return jsonify({"error": "Class is full."}), 400

    # Add booking
    fitness_class['booked_members'].append(member_name)

    # Save to file
    with open('classes_db.json', 'w') as file:
        json.dump(classes_db, file)

    return jsonify({"message": "Booking successful."}), 200



@app.route('/classes/<int:class_id>/members', methods=['GET'])
def view_members(class_id):

    user_role = request.headers.get('Role')

    # Only Admin or Trainer allowed
    if user_role not in ['Admin', 'Trainer']:
        return jsonify({"error": "Unauthorized: Only Admins or Trainers can view member list."}), 403

    # Find class
    fitness_class = next((c for c in classes_db if c['id'] == class_id), None)

    if not fitness_class:
        return jsonify({"error": "Class not found."}), 404

    # If no members booked
    if not fitness_class.get('booked_members'):
        return jsonify({"message": "No members have booked this class yet."}), 200

    return jsonify({
        "class_id": class_id,
        "booked_members": fitness_class['booked_members']
    }), 200



if __name__ == '__main__':
    app.run(debug=True, port=5000)