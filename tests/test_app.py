import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create fresh tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests

def test_add_user(client):
    response = client.get("/add_user/TestUser")
    assert b"Added TestUser to the database!" in response.data
    with app.app_context():
        users = User.query.all()
        assert len(users) == 1
        assert users[0].name == "TestUser"

def test_list_users(client):
    with app.app_context():
        user1 = User(name="User1")
        user2 = User(name="User2")
        db.session.add_all([user1, user2])
        db.session.commit()

    response = client.get("/list_users")
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "User1"
    assert data[1]["name"] == "User2"

def test_edit_user(client):
    with app.app_context():
        user = User(name="OldName")
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Capture user ID within the context

    response = client.get(f"/edit_user/{user_id}/NewName")
    assert b"Updated User" in response.data
    with app.app_context():
        updated_user = db.session.get(User, user_id)  # Use db.session.get()
        assert updated_user.name == "NewName"

def test_delete_user(client):
    with app.app_context():
        user = User(name="ToDelete")
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Capture user ID within the context

    response = client.get(f"/delete_user/{user_id}")
    assert b"Deleted User" in response.data
    with app.app_context():
        deleted_user = db.session.get(User, user_id)  # Use db.session.get()
        assert deleted_user is None

def test_get_user(client):
    with app.app_context():
        user = User(name="TestUser")
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Capture user ID within the context

    response = client.get(f"/get_user/{user_id}")
    data = response.get_json()
    assert data["name"] == "TestUser"

