# FastAPI JWT RBAC

Simple API with JWT Authentication and Role-Based Access Control using FastAPI and PostgreSQL.

## Installation Steps


1. (Recommended) Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL database:
```bash
createdb fastapi_rbac
```

4. Run the application (from the parent directory):
```bash
uvicorn fastapi_jwt_rbac.main:app --reload
```

## Endpoints

1. **POST /register** - Register a user
   - Body: `{ "username": "example", "password": "password123", "role": "user" }`

2. **POST /login** - Login user
   - Body: `{ "username": "example", "password": "password123" }`
   - Response: `{ "access_token": "JWT_TOKEN", "token_type": "bearer" }`

3. **GET /projects** - Get all projects (requires JWT)

4. **POST /projects** - Create project (admin only, requires JWT)
   - Body: `{ "name": "Project A", "description": "Description of project" }`

5. **DELETE /projects/{project_id}** - Delete project (admin only, requires JWT)
   - Response: `{ "detail": "Project deleted" }`

## Dependencies

- FastAPI
- SQLModel  
- PostgreSQL
- JWT (python-jose)
- bcrypt (passlib)

## Usage

The API implements:
- User registration and login with bcrypt password hashing
- JWT tokens with user ID and role information
- Role-based access control (admin and user roles)
- CRUD operations for projects with proper permissions (admin can create/delete, users can view)
- PostgreSQL database with SQLModel ORM
