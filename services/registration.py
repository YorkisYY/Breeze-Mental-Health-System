import os
import pandas as pd
import re
from model.user import User
from config import USER_DATA_PATH
from datetime import datetime

# Function to validate email format
def is_valid_email(email):
    """Validate email format using a regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Check if the username is unique for a specific role
def is_username_unique(username, role):
    if os.path.exists(USER_DATA_PATH):
        df = pd.read_csv(USER_DATA_PATH)
        if not df[(df['username'] == username) & (df['role'] == role)].empty:
            return False
    return True

def register_user():
    # Prompt user to enter username and password
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Ensure username and password are not empty
    if not username or not password:
        print("Username and password cannot be empty.")
        return True

    # Prompt user for email until valid email is provided
    while True:
        email = input("Enter email: ").strip()
        if is_valid_email(email):
            break
        print("Invalid email format. Please try again.")

    # Prompt user for emergency email until valid email is provided
    while True:
        emergency_email = input("Enter emergency contact email: ").strip()
        if is_valid_email(emergency_email):
            break
        print("Invalid emergency email format. Please try again.")

    # Display available roles
    print("\nAvailable roles:")
    print("1. Patient")
    print("2. Mental Health Wellbeing Personnel")
    print("3. Admin")
    role_choice = input("\nSelect role (1-3): ").strip()

    roles = {
        "1": "patient",
        "2": "mhwp",
        "3": "admin"
    }

    if role_choice not in roles:
        print("Invalid role selection.")
        return True

    role = roles[role_choice]

    # For special roles, require verification code
    if role in ["admin", "mhwp"]:
        verification_code = input(f"Enter {role} registration code: ").strip()
        # Replace "0000" with dynamic configuration for better security
        if verification_code != "0000":
            print(f"Invalid {role} code. Registration failed.")
            return True

    # Check if the username is unique
    if not is_username_unique(username, role):
        print(f"Username '{username}' already exists for role '{role}'.")
        return True

    # Create a new user instance and save it
    new_user = User(username, password, role, email, emergency_email)
    if new_user.save_to_csv():
        print("User registration successful!")
    else:
        print("Registration failed.")
    return True