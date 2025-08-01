from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fastapi_rbac")
# plz use "postgresql+psycopg2://postgres:password@localhost:5432/fastapi_rbac" if you are using psycopg2 while evaualating for my submission.
engine = create_engine(DATABASE_URL)

# Simple  Security I made just for this project
SECRET_KEY = "secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Simple model for less confusion
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False)
    hashed_password: str
    role: str

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    created_by: int = Field(foreign_key="user.id")

# Dont think this AI 
class UserRegister(SQLModel):
    username: str
    password: str
    role: str

class UserLogin(SQLModel):
    username: str
    password: str

class ProjectCreate(SQLModel):
    name: str
    description: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# FastAPI app
app = FastAPI()

# Database session
def get_session():
    with Session(engine) as session:
        yield session

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        if username == "":
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Startup
@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Endpoints
@app.post("/register")
def register(user: UserRegister, session: Session = Depends(get_session)):
    # Check if user exists
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role}

@app.post("/login")
def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_credentials.username)).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="The username or password is incorrect")
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/projects")
def get_projects(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return projects

@app.post("/projects")
def create_project(project: ProjectCreate, current_user: User = Depends(require_admin), session: Session = Depends(get_session)):
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="Current user ID is missing.")
    db_project = Project(name=project.name, description=project.description, created_by=current_user.id)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

# Delete project endpoint (admin only)
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(require_admin), session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"detail": "Project deleted"}
