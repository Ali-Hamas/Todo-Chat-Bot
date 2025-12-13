import requests
import json

# Test the API endpoints
BASE_URL = "http://127.0.0.1:8000"

print("Testing the Todo API...")

# Test the root endpoint
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Error accessing root endpoint: {e}")

# Test the /api/chat endpoint (this will fail without auth)
try:
    chat_data = {
        "message": "Hello, can you help me?",
        "conversation_id": None
    }
    response = requests.post(f"{BASE_URL}/api/chat",
                           json=chat_data,
                           headers={"Content-Type": "application/json"})
    print(f"Chat endpoint (without auth): {response.status_code}")
    if response.status_code == 401:
        print("  - Expected: Unauthorized (requires authentication)")
    else:
        print(f"  - Response: {response.text}")
except Exception as e:
    print(f"Error accessing chat endpoint: {e}")

# Test tasks endpoint (this will also fail without auth)
try:
    response = requests.get(f"{BASE_URL}/api/tasks")
    print(f"Tasks endpoint (without auth): {response.status_code}")
    if response.status_code == 401:
        print("  - Expected: Unauthorized (requires authentication)")
except Exception as e:
    print(f"Error accessing tasks endpoint: {e}")

print("\nNote: Most endpoints require authentication. You need to register/login first.")
print("To test fully, you can use the frontend at http://localhost:3000 after starting it.")