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

# API Documentation

## Overview
This document provides an overview of the API routes and services available in the `genadam` application. Each section corresponds to a route or service module, detailing the functionality, HTTP methods, and expected input/output.

---

## Routes

### Admin Routes (`app/routes/admin.py`)
**Purpose:** Handles administrative functions.

#### Endpoints:
1. **`GET /admin/analytics`**
   - **Description:** Fetches analytics data for the admin dashboard.
   - **Input:** None
   - **Output:**
     ```json
     {
       "userCount": 100,
       "transactions": 2000,
       "activeSessions": 45
     }
     ```

2. **`POST /admin/accounts`**
   - **Description:** Allows admin to manage user accounts (create, update, delete).
   - **Input:**
     ```json
     {
       "action": "create",
       "user": {
         "name": "John Doe",
         "email": "john.doe@example.com"
       }
     }
     ```
   - **Output:**
     ```json
     {
       "message": "Account created successfully",
       "userId": 12345
     }
     ```

---

### Authentication Routes (`app/routes/auth.py`)
**Purpose:** Manages user authentication and authorization.

#### Endpoints:
1. **`POST /auth/login`**
   - **Description:** Authenticates a user and generates a token.
   - **Input:**
     ```json
     {
       "email": "john.doe@example.com",
       "password": "password123"
     }
     ```
   - **Output:**
     ```json
     {
       "token": "abcd1234",
       "expiresIn": 3600
     }
     ```

2. **`POST /auth/register`**
   - **Description:** Registers a new user.
   - **Input:**
     ```json
     {
       "name": "John Doe",
       "email": "john.doe@example.com",
       "password": "password123"
     }
     ```
   - **Output:**
     ```json
     {
       "message": "User registered successfully",
       "userId": 12345
     }
     ```

---

### Catalog Routes (`app/routes/catalog.py`)
**Purpose:** Manages dataset catalog operations.

#### Endpoints:
1. **`GET /catalog`**
   - **Description:** Retrieves all available datasets.
   - **Input:** None
   - **Output:**
     ```json
     [
       {
         "datasetId": 1,
         "name": "Dataset A",
         "description": "Description of Dataset A"
       },
       {
         "datasetId": 2,
         "name": "Dataset B",
         "description": "Description of Dataset B"
       }
     ]
     ```

2. **`POST /catalog/register`**
   - **Description:** Allows data producers to register a new dataset.
   - **Input:**
     ```json
     {
       "name": "Dataset C",
       "description": "Description of Dataset C",
       "owner": "Producer Name"
     }
     ```
   - **Output:**
     ```json
     {
       "message": "Dataset registered successfully",
       "datasetId": 3
     }
     ```

---

### User Routes (`app/routes/user.py`)
**Purpose:** Manages user-specific actions.

#### Endpoints:
1. **`GET /user/profile`**
   - **Description:** Retrieves the user profile.
   - **Input:** Authentication token
   - **Output:**
     ```json
     {
       "userId": 12345,
       "name": "John Doe",
       "email": "john.doe@example.com"
     }
     ```

2. **`PUT /user/profile`**
   - **Description:** Updates the user profile.
   - **Input:**
     ```json
     {
       "name": "Johnathan Doe",
       "email": "john.doe@example.com"
     }
     ```
   - **Output:**
     ```json
     {
       "message": "Profile updated successfully"
     }
     ```

---

## Services

### Lineage Service (`app/services/lineage.py`)
**Purpose:** Tracks the lineage of datasets, including transformations and data sources.

#### Functions:
1. `get_lineage(dataset_id: int)`
   - **Description:** Retrieves lineage information for a specific dataset.
   - **Input:** Dataset ID
   - **Output:**
     ```json
     {
       "datasetId": 1,
       "lineage": [
         "Source A",
         "Transformation B",
         "Dataset A"
       ]
     }
     ```

---

### Metadata Service (`app/services/metadata.py`)
**Purpose:** Handles metadata registration and retrieval.

#### Functions:
1. `register_metadata(metadata: dict)`
   - **Description:** Registers metadata for a dataset.
   - **Input:** Metadata dictionary
   - **Output:**
     ```json
     {
       "message": "Metadata registered successfully"
     }
     ```

2. `get_metadata(dataset_id: int)`
   - **Description:** Retrieves metadata for a dataset.
   - **Input:** Dataset ID
   - **Output:**
     ```json
     {
       "datasetId": 1,
       "metadata": {
         "owner": "Producer Name",
         "createdAt": "2024-12-23",
         "fields": [
           "Field A",
           "Field B"
         ]
       }
     }
     ```

---

### Quality Service (`app/services/quality.py`)
**Purpose:** Ensures data quality by running checks and validations.

#### Functions:
1. `validate_dataset(dataset_id: int)`
   - **Description:** Runs quality checks on a dataset.
   - **Input:** Dataset ID
   - **Output:**
     ```json
     {
       "datasetId": 1,
       "qualityScore": 95,
       "issues": []
     }
     ```

---

### Observability Service (`app/services/observability.py`)
**Purpose:** Monitors application performance and generates logs.

#### Functions:
1. `log_event(event: dict)`
   - **Description:** Logs an event.
   - **Input:** Event dictionary
   - **Output:**
     ```json
     {
       "message": "Event logged successfully"
     }
     ```

---

## Notes
- Authentication tokens are required for all routes except `/auth/login` and `/auth/register`.
- Ensure appropriate HTTP headers and status codes are returned for each endpoint.
- Refer to the `config.py` for adjustable parameters such as database connections and API keys.


