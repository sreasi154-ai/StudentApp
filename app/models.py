from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object without binding it to a specific app yet.
# This prevents circular imports when your app grows.
db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'  # Sets the table name inside MySQL
    
    # Defining table columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name=db.column(db.string(50),nullable=False)
    blood_group = db.Column(db.String(5), nullable=True)
    course = db.Column(db.String(100), nullable=True)
    stream = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
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
        return{
            "id":self.id,
            "first_name":self.first_name,
            "last_name":self.last_name,
            "blood_group":self.blood_group,
            "admission_year": self.admission_year,
            "course": self.course,
            "stream": self.stream,
            "email": self.email,
            "contact_number": self.contact_number,
            "guardians_name": self.guardians_name,
            "guardians_contact_number": self.guardians_contact_number,
            "current_address": self.current_address,
            "permanent_address": self.permanent_address,
            "medical_fitness": self.medical_fitness,
            "account_created_date": self.account_created_date.isoformat() if self.account_created_date else None,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None
        }