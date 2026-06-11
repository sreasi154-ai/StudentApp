from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  
    user_type = db.Column(db.Enum('admin', 'student', name='user_types'), nullable=False, default='student')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # FIXED: Ensured 'Student' is passed as a string literal to prevent forward-reference errors
    student_profile = db.relationship('Student', backref='user_account', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.user_type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "user_type": self.user_type,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Student(db.Model):
    __tablename__ = 'students' 
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # VERIFIED: Linked via users.id column string
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)  
    blood_group = db.Column(db.String(5), nullable=True)
    course = db.Column(db.String(100), nullable=True)
    stream = db.Column(db.String(100), nullable=True)
    contact_number = db.Column(db.String(15), nullable=False)
    guardians_name = db.Column(db.String(100), nullable=True)
    guardians_contact_number = db.Column(db.String(15), nullable=True)
    current_address = db.Column(db.Text, nullable=True)         
    permanent_address = db.Column(db.Text, nullable=True)       
    medical_fitness = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "blood_group": self.blood_group,
            "course": self.course,
            "stream": self.stream,
            "email": self.email,
            "contact_number": self.contact_number,
            "guardians_name": self.guardians_name,
            "guardians_contact_number": self.guardians_contact_number,
            "current_address": self.current_address,
            "permanent_address": self.permanent_address,
            "medical_fitness": self.medical_fitness,
            "age": self.age,
            "created_at": self.created_at.isoformat() if self.created_at else None  
        }