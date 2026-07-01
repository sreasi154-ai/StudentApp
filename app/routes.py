from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from .models import db, User, Student

# Create a Blueprint for our API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request payload. JSON data required."}), 400

    # Extract required fields
    password = data.get('password')
    email = data.get('email')
    is_admin=data.get('is_admin',False)

    if is_admin:
        if not all([password,email]):
            return jsonify({"error":"Missing mandatory admin fields:email,password"}),400
        user_role='admin'
    else:
        user_role='student'
        first_name=data.get('first_name')
        last_name=data.get('last_name')
        contact_number=data.get('contact_number')

        if not all([password, email, first_name, last_name, contact_number]):
            return jsonify({"error": "Missing mandatory fields: password, email, first_name, last_name, contact_number"}), 400

    # Prevent duplicates using modern db.select syntax
    if db.session.scalar(db.select(User).filter_by(email=email)):
        return jsonify({"error": f"A user account with email '{email}' already exists."}), 409
    

    try:
        # Step A: Create and Hash the User Account
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            email=email,
            password_hash=hashed_password,
            user_type=user_role,
            is_active=True
        )
        db.session.add(new_user)
        new_student=None

        if user_role == 'student':
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
            "student": new_student.to_dict() if new_student is not None else None
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500
    

@api_bp.route('/api/students', methods=['GET'])
def get_students():
    # Fallback default values if parameters are missing or incorrect
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int) 

    try:
        # 1. Build a modern Select statement ordered by creation date or ID 
        # (This prevents row skipping/shuffling across pages)
        stmt = db.select(Student).order_by(Student.id.desc())
        
        # 2. Use db.paginate instead of legacy Model.query.paginate
        paginated_data = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        
        # 3. paginated_data.items contains the list of Student objects for this specific page
        student_list = [s.to_dict() for s in paginated_data.items]
        
        return jsonify({
            "total_students": paginated_data.total,      
            "current_page": paginated_data.page,         
            "per_page": paginated_data.per_page,         
            "total_pages": paginated_data.pages,         
            "has_next": paginated_data.has_next,         
            "has_prev": paginated_data.has_prev,         
            "students": student_list                    
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500
    

@api_bp.route('/api/students/<int:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    try:
        # 1. Fetch the student using the modern db.select syntax by primary key id
        student = db.session.scalar(db.select(Student).filter_by(id=student_id))
        
        # Fallback to user_id just in case
        if not student:
            student = db.session.scalar(db.select(Student).filter_by(user_id=student_id))

        # 2. CLIENT ERROR: Return 404 if the student doesn't exist
        if not student:  
            return jsonify({"error": f"Student with ID {student_id} not found."}), 404
            
        # 3. SUCCESS: Return the single student data
        return jsonify({
            "message": "Student record retrieved successfully.",
            "student": student.to_dict()
        }), 200

    except Exception as e:
        # SERVER ERROR: Catch unexpected system or database crashes
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@api_bp.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        # 1. Fetch the student profile using modern syntax
        student = db.session.scalar(db.select(Student).filter_by(id=student_id))
        
        # 2. CLIENT ERROR: Return 404 if the student doesn't exist
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found."}), 404

        # 3. Get the incoming JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request payload. JSON data required."}), 400

        # 4. Optional: Handle unique constraint checks if email is being updated
        new_email = data.get('email')
        if new_email and new_email != student.email:
            existing_email = db.session.scalar(db.select(Student).filter_by(email=new_email))
            if existing_email:
                return jsonify({"error": f"A student profile with email '{new_email}' already exists."}), 409

        # Validate required fields are not explicitly set to empty strings
        if 'first_name' in data and not str(data['first_name']).strip():
            return jsonify({"error": "First name cannot be empty."}), 400
        if 'last_name' in data and not str(data['last_name']).strip():
            return jsonify({"error": "Last name cannot be empty."}), 400
        if 'contact_number' in data and not str(data['contact_number']).strip():
            return jsonify({"error": "Contact number cannot be empty."}), 400

        # 5. Dynamically update Student fields if they are provided in the JSON body
        # (Using .get() with the current value as a fallback keeps existing data intact)
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.email = data.get('email', student.email)
        student.contact_number = data.get('contact_number', student.contact_number)
        student.blood_group = data.get('blood_group', student.blood_group)
        student.course = data.get('course', student.course)
        student.stream = data.get('stream', student.stream)
        student.guardians_name = data.get('guardians_name', student.guardians_name)
        student.guardians_contact_number = data.get('guardians_contact_number', student.guardians_contact_number)
        student.current_address = data.get('current_address', student.current_address)
        student.permanent_address = data.get('permanent_address', student.permanent_address)
        student.medical_fitness = data.get('medical_fitness', student.medical_fitness)
        student.age = data.get('age', student.age)

        # 6. Commit the updates safely
        db.session.commit()
        
        return jsonify({
            "message": "Student profile updated successfully!",
            "student": student.to_dict()
        }), 200

    except Exception as e:
        # SERVER ERROR: Rollback database updates if something crashes
        db.session.rollback()
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@api_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        # 1. Fetch the student profile using modern syntax
        student = db.session.scalar(db.select(Student).filter_by(id=student_id))
        
        # 2. CLIENT ERROR: Return 404 if the student doesn't exist
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found."}), 404
        
        user=db.session.scalar(db.select(User).filter_by(id=student.user_id))

        # 3. Delete the student profile (cascades to user account if set up)
        db.session.delete(student)
        if user:
            db.session.delete(user)  

        db.session.commit()
        return jsonify({"message": f"Student with ID {student_id} and associated user account deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500
           

@api_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request payload. JSON data required."}), 400

    email = data.get('email')  # Accept 'email' as the login identifier
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Both 'email' and 'password' fields are required."}), 400

    try:

        user = db.session.scalar(db.select(User).filter_by(email=email))
        if not user:
            return jsonify({"error": "Invalid email or password."}), 401

        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password."}), 401
        
        if not user.is_active:
            return jsonify({"error": "This account has been deactivated."}), 403

        # 5. Fetch associated Student profile payload if user type matches
        student_data = None
        first_name=""
        last_name=""
        if user.user_type == 'student':
            student = db.session.scalar(db.select(Student).filter_by(user_id=user.id))
            if student:
                student_data = student.to_dict()
                first_name=student.first_name
                last_name=student.last_name

        user_payload = user.to_dict()
        user_payload["first_name"] = first_name
        user_payload["last_name"] = last_name

        # 6. Return standard success response without tokens
        return jsonify({
            "message": "Login successful!",
            "user": user_payload,
            "student": student_data
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500

@api_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        total_students = db.session.scalar(db.select(db.func.count(Student.id))) or 0
        active_users = db.session.scalar(db.select(db.func.count(User.id)).filter_by(is_active=True)) or 0
        # For courses, we will count distinct courses in student table
        courses = db.session.scalar(db.select(db.func.count(db.distinct(Student.course)))) or 0
        
        # Fetch some recent students for the spotlight
        recent_students_query = db.select(Student).order_by(Student.id.desc()).limit(6)
        recent_students = db.session.scalars(recent_students_query).all()
        
        students_data = []
        import random
        # Warm palette for frontend
        bg_colors = ['#D97706', '#B45309', '#4B7C59', '#92400E', '#7C5B3A', '#65793D']
        
        for idx, student in enumerate(recent_students):
            initials = ""
            if student.first_name: initials += student.first_name[0]
            if student.last_name: initials += student.last_name[0]
            
            # Generating fake grade and attendance for visualization
            students_data.append({
                "initials": initials.upper(),
                "name": f"{student.first_name} {student.last_name}",
                "course": student.course or 'General',
                "grade": random.choice(['A+', 'A', 'A-', 'B+', 'B']),
                "bg": bg_colors[idx % len(bg_colors)],
                "attendance": random.randint(85, 100)
            })

        stats = [
            { "value": str(total_students), "label": 'Total Students', "icon": 'pi pi-users' },
            { "value": str(courses), "label": 'Courses Enrolled', "icon": 'pi pi-book' },
            { "value": str(active_users), "label": 'Active Accounts', "icon": 'pi pi-star-fill' },
            { "value": '200+', "label": 'Institutions', "icon": 'pi pi-building' },
        ]

        return jsonify({
            "stats": stats,
            "students": students_data
        }), 200

    except Exception as e:
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500