# GenAdam API Documentation

## Base URL
`http://127.0.0.1:5001`

## Endpoints
### 1. Add User
**URL:** `/add_user/<name>`  
**Method:** GET  
**Description:** Adds a new user to the database.  
**Response:**  
- Success: `Added <name> to the database!`

### 2. List Users
**URL:** `/list_users`  
**Method:** GET  
**Description:** Returns a list of all users.  
**Response Example:**
```json
[
  {"id": 1, "name": "User1"},
  {"id": 2, "name": "User2"}
]

