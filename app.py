from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use absolute path to ensure database file is created in the correct location
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Home route
@app.route("/")
def hello():
    return "SQLite is working!"

# List all users
@app.route("/list_users")
def list_users():
    users = User.query.all()
    return "<br>".join([f"ID: {user.id}, Name: {user.name}" for user in users])

# Add a user with a specified name
@app.route("/add_user/<name>")
def add_user(name):
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    return f"Added {new_user.name} to the database!"

# Edit an existing user's name by ID
@app.route("/edit_user/<int:id>/<new_name>")
def edit_user(id, new_name):
    user = User.query.get(id)
    if user:
        user.name = new_name
        db.session.commit()
        return f"Updated User {id} to {new_name}"
    else:
        return f"User {id} not found!"

# Delete a user by ID
@app.route("/delete_user/<int:id>")
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"Deleted User {id}"
    else:
        return f"User {id} not found!"

# Test route to add a default user
@app.route("/users")
def users():
    try:
        new_user = User(name="Test User")
        db.session.add(new_user)
        db.session.commit()
        return f"Added {new_user.name} to the database!"
    except Exception as e:
        return f"Error: {e}"

# Main block
if __name__ == "__main__":
    try:
        with app.app_context():
            print("Attempting to create database tables...")
            db.create_all()  # Creates the tables
            print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    # Start the Flask app
    app.run(debug=True, port=5001)

