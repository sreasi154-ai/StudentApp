import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from .models import db
from sqlalchemy.exc import OperationalError  # Imported to catch database connection errors

def create_app():
    app = Flask(__name__)
    
    # 1. Database Configuration for Local MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQL%40123@localhost:3306/student_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)  # Enable CORS for all routes and origins
    
    # Initialize DB
    db.init_app(app)
    
    # 2. Setup Logging
    configure_logging(app)
    
    with app.app_context():
        # CRITICAL: Import your models here so Flask-SQLAlchemy registers them for create_all()
        from .models import Student, User 
        
        # --- Import and Register your API Routes Blueprint ---
        from .routes import api_bp
        app.register_blueprint(api_bp)
        # ---------------------------------------------------------
        
        try:
            # Send a simple ping query to verify the connection is alive
            db.session.execute(db.text('SELECT 1'))
            app.logger.info("Successfully connected to the MySQL database server.")
            
            # ----------------------------------------------------
            # --- Initialize Tables ---
            # ----------------------------------------------------
            app.logger.info("Initializing database tables...")
          
            db.create_all() # This creates tables if they don't exist
            app.logger.info("MySQL database tables initialized successfully.")
            
        except OperationalError as e:
            app.logger.error("CRITICAL: Failed to connect to the MySQL database!")
            app.logger.error(f"Error Details: {e.orig}")
        except Exception as e:
            app.logger.error(f"An unexpected error occurred during database setup: {e}")
        # ----------------------------------------------------
        
    return app

def configure_logging(app):
    """Configures application-wide logging."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s (%(pathname)s:%(lineno)d)')
    
    # File Handler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Stream Handler (Console/Terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info("Logging initialized successfully.")