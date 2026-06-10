# run.py
from app import create_app  # Import the factory function from your app package

# Call the function to create the fully configured Flask app
app = create_app()

if __name__ == '__main__':
    print("------------ APPLICATION HAS STARTED AT ::: 127.0.0.1:5000 ------------")
    app.run(debug=True, host='127.0.0.1', port=5000)