from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use absolute path to ensure database file is created in the correct location
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

@app.route("/")
def hello():
    return "SQLite is working!"

@app.route("/list_users")
def list_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name} for user in users])

@app.route("/add_user/<name>")
def add_user(name):
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    return f"Added {new_user.name} to the database!"

@app.route("/edit_user/<int:id>/<new_name>")
def edit_user(id, new_name):
    user = db.session.get(User, id)  # Use db.session.get()
    if user:
        user.name = new_name
        db.session.commit()
        return f"Updated User {id} to {new_name}"
    else:
        return f"User {id} not found!"

@app.route("/delete_user/<int:id>")
def delete_user(id):
    user = db.session.get(User, id)  # Use db.session.get()
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"Deleted User {id}"
    else:
        return f"User {id} not found!"

@app.route("/get_user/<int:id>")
def get_user(id):
    user = db.session.get(User, id)  # Use db.session.get()
    if user:
        return jsonify({"id": user.id, "name": user.name})
    else:
        return f"User {id} not found!"

if __name__ == "__main__":
    try:
        with app.app_context():
            print("Attempting to create database tables...")
            db.create_all()
            print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

    app.run(debug=True, port=5001)



