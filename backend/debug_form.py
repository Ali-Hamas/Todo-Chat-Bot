import requests

# Test form submission with explicit content-type
BASE_URL = "http://127.0.0.1:8000"

print("Debugging form submission...")

# Test with requests using different approaches
try:
    # Approach 1: Using data parameter (should automatically set content-type)
    print("\n1. Using requests with data parameter:")
    response1 = requests.post(
        f"{BASE_URL}/auth/register",
        data={
            "email": "debug@example.com",
            "password": "debugpass",
            "name": "Debug User"
        }
    )
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.text}")

    # Approach 2: Using requests with explicit headers
    print("\n2. Using requests with explicit form content-type:")
    response2 = requests.post(
        f"{BASE_URL}/auth/register",
        data="email=test3@example.com&password=testpass&name=Test3",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")

    # Approach 3: Using files parameter to force form encoding
    print("\n3. Using requests with files parameter (to force form encoding):")
    response3 = requests.post(
        f"{BASE_URL}/auth/register",
        files={
            'email': (None, 'filetest@example.com'),
            'password': (None, 'filetestpass'),
            'name': (None, 'File Test User')
        }
    )
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text}")

except Exception as e:
    print(f"Error during testing: {e}")