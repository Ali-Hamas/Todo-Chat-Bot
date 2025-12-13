import requests
import json

# Test script with JSON data since endpoints are now more flexible
BASE_URL = "http://127.0.0.1:8000"

print("Testing API with JSON data (now that endpoints are flexible)...")

# Step 1: Register a test user with JSON
print("\n1. Registering a test user with JSON...")
try:
    register_data = {
        "email": "json_test@example.com",
        "password": "json_testpassword",
        "name": "JSON Test User"
    }
    register_response = requests.post(f"{BASE_URL}/auth/register",
                                   json=register_data,
                                   headers={"Content-Type": "application/json"})
    print(f"Registration response: {register_response.status_code}")
    print(f"Registration response text: {register_response.text}")

    if register_response.status_code == 200:
        auth_data = register_response.json()
        access_token = auth_data.get("access_token")
        print("Successfully registered and got access token")
    else:
        print("Registration failed")

        # Try logging in instead (in case user already exists from previous attempts)
        print("\nTrying to login with JSON...")
        login_data = {
            "email": "json_test@example.com",
            "password": "json_testpassword"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login",
                                     json=login_data,
                                     headers={"Content-Type": "application/json"})
        print(f"Login response: {login_response.status_code}")
        print(f"Login response text: {login_response.text}")

        if login_response.status_code == 200:
            auth_data = login_response.json()
            access_token = auth_data.get("access_token")
            print("Successfully logged in and got access token")
        else:
            print("Login failed")
            access_token = None

except Exception as e:
    print(f"Error during auth: {e}")
    access_token = None

if access_token:
    # Step 2: Use the token to call protected endpoints
    print("\n2. Testing chat endpoint with authentication...")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    try:
        chat_data = {
            "message": "Hello, can you help me add a task?",
            "conversation_id": None
        }
        chat_response = requests.post(f"{BASE_URL}/api/chat",
                                   json=chat_data,
                                   headers=headers)
        print(f"Chat endpoint response: {chat_response.status_code}")
        if chat_response.status_code == 200:
            print(f"Chat response: {chat_response.json()}")
        else:
            print(f"Chat error: {chat_response.text}")
    except Exception as e:
        print(f"Error calling chat endpoint: {e}")

    # Step 3: Test tasks endpoint
    print("\n3. Testing tasks endpoint with authentication...")
    try:
        tasks_response = requests.get(f"{BASE_URL}/api/tasks",
                                    headers=headers)
        print(f"Tasks endpoint response: {tasks_response.status_code}")
        if tasks_response.status_code == 200:
            print(f"Tasks response: {tasks_response.json()}")
        else:
            print(f"Tasks error: {tasks_response.text}")
    except Exception as e:
        print(f"Error calling tasks endpoint: {e}")
else:
    print("\nCould not get access token, cannot test protected endpoints")

print("\nIf this works, the frontend should now be able to communicate properly with authentication.")