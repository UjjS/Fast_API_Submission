import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing FastAPI JWT RBAC")
    
    # Test user registration
    print("1. Testing user registration...")
    user_data = {
        "username": "example", 
        "password": "password123",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    
    # Test admin registration  
    print("2. Testing admin registration...")
    admin_data = {
        "username": "admin",
        "password": "adminpass123", 
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/register", json=admin_data)
    print(f"Status: {response.status_code}")
    
    # Test login
    print("3. Testing login...")
    login_data = {
        "username": "example",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Got token: {token[:50]}...")
        
        # Test get projects
        print("4. Testing get projects...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        print(f"Status: {response.status_code}")
        
        # Test create project (should fail for regular user)
        print("5. Testing create project as user (should fail)...")
        project_data = {
            "name": "Project A",
            "description": "Description of project"
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
        print(f"Status: {response.status_code}")
        
    # Test admin login and create project
    print("6. Testing admin login...")
    admin_login = {
        "username": "admin",
        "password": "adminpass123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login)
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("7. Testing create project as admin...")
        response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=admin_headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Created project: {response.json()}")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
