from flask import Flask, request, jsonify

app = Flask(__name__)

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
        "created_by": user_role
    }
    
    classes_db.append(new_class)

    return jsonify({"message": "Class created successfully", "class": new_class}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)