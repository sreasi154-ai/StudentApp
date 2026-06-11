from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from .models import db, User, Student

# Create a Blueprint for our API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request payload. JSON data required."}), 400

    # Extract required fields
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact_number = data.get('contact_number')

    if not all([username, password, email, first_name, last_name, contact_number]):
        return jsonify({"error": "Missing mandatory fields: username, password, email, first_name, last_name, contact_number"}), 400

    # Prevent duplicates
    if User.query.filter_by(username=username).first():
        return jsonify({"error": f"Username '{username}' is already taken."}), 409
    if Student.query.filter_by(email=email).first():
        return jsonify({"error": f"A student profile with email '{email}' already exists."}), 409

    try:
        # Step A: Create and Hash the User Account
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            username=username,
            password_hash=hashed_password,
            user_type='student',
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush()  # Grabs the new_user.id instantly

        # Step B: Create Student Profile linked to User Account
        new_student = Student(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact_number=contact_number,
            blood_group=data.get('blood_group'),
            course=data.get('course'),
            stream=data.get('stream'),
            guardians_name=data.get('guardians_name'),
            guardians_contact_number=data.get('guardians_contact_number'),
            current_address=data.get('current_address'),
            permanent_address=data.get('permanent_address'),
            medical_fitness=data.get('medical_fitness'),
            age=data.get('age')
        )
        db.session.add(new_student)

        # Step C: Commit Both cleanly
        db.session.commit()
        
        return jsonify({
            "message": "Student registered successfully!",
            "user": new_user.to_dict(),
            "student": new_student.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500