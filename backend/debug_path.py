import sys
import os

# Calculated parent path
current = os.path.abspath(__file__)
parent = os.path.dirname(os.path.dirname(current))

print(f"Current file: {current}")
print(f"Calculated parent: {parent}")

# Append to sys.path
sys.path.append(parent)
print("sys.path modified.")

# Check if parent string is in sys.path
if parent in sys.path:
    print(f"Confirmed: {parent} is in sys.path")
else:
    print("Warning: Parent path not found in sys.path")

try:
    import backend
    print(f"Successfully imported backend: {backend}")
    import backend.models
    print(f"Successfully imported backend.models: {backend.models}")
    from backend.models.todo_models import User
    print(f"Successfully imported User from backend.models.todo_models")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
