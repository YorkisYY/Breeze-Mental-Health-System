import os
import pandas as pd
from model.user import User
from config import USER_DATA_PATH

# Check if the username is unique for a specific role
def is_username_unique(username, role):
    if os.path.exists(USER_DATA_PATH):
        # Read the existing CSV file
        df = pd.read_csv(USER_DATA_PATH)
        # Check if a row exists with the same username and role
        if not df[(df['username'] == username) & (df['role'] == role)].empty:
            return False  # Username is not unique
    return True  # Username is unique

# Function to handle user registration
def register_user():
    # Prompt user to enter username and password
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Display available roles for the user to select
    print("\nAvailable roles:")
    print("1. Patient")  
    print("2. Mental Health Wellbeing Personnel")
    print("3. Admin")
    role_choice = input("\nSelect role (1-4): ").strip()

    # Mapping role choices to their corresponding role strings
    roles = {
        "1": "patient",
        "2": "mhwp",  # Mental Health Worker
        "3": "admin"
    }

    # Validate the role choice
    if role_choice not in roles:
        print("Invalid role selection.")
        return True

    role = roles[role_choice]  # Get the corresponding role string

    # Ensure username and password are not empty
    if not username or not password:
        print("Username and password cannot be empty.")
        return True

    # For special roles, require a verification code
    if role in ["admin", "mhwp"]:
        verification_code = input(f"Enter {role} registration code: ").strip()
        # Verify the code (currently set to "0000" for all roles)
        if verification_code != "0000":
            print(f"Invalid {role} code. Registration failed.")
            return True

    # Check if the username is unique for the selected role
    if not is_username_unique(username, role):
        print(f"Username '{username}' already exists for role '{role}'.")
        return True

    # Create a new user instance and save it to the CSV file
    new_user = User(username, password, role)
    new_user.save_to_csv()
    print("Registration successful!")
    return True
