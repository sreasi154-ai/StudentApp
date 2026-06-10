import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from .models import db
from sqlalchemy.exc import OperationalError  # Imported to catch database connection errors

def create_app():
    app = Flask(__name__)
    
    # 1. Database Configuration for Local MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQL%40123@localhost:3306/student_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize DB
    db.init_app(app)
    
    # 2. Setup Logging
    configure_logging(app)
    
    with app.app_context():
        # --- NEW: Database Connection Verification Check ---
        try:
            # Send a simple ping query to verify the connection is alive
            db.session.execute(db.text('SELECT 1'))
            app.logger.info("Successfully connected to the MySQL database server.")
            
            # If connection is successful, proceed with creating tables
            db.create_all()
            app.logger.info("MySQL database tables verified/initialized successfully.")
            
        except OperationalError as e:
            # This catches wrong password, wrong host, or stopped server errors
            app.logger.error("CRITICAL: Failed to connect to the MySQL database!")
            app.logger.error(f"Error Details: {e.orig}")
            # Optional: system exit if you don't want the app to run without a working DB
            # import sys; sys.exit(1)
        except Exception as e:
            # Catch-all for any other unexpected database issues
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