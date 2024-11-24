import os
import pandas as pd
from model.user import User

# File path to store user data
FILE_PATH = "patient_data.csv"

# Initialize the CSV file with default headers if it doesn't already exist
def initialize_csv(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            # Write the CSV headers: username, password, and role
            f.write("username,password,role\n")

# Check if the username is unique for a specific role
def is_username_unique(username, role, file_path):
    if os.path.exists(file_path):
        # Read the existing CSV file
        df = pd.read_csv(file_path)
        # Check if a row exists with the same username and role
        if not df[(df['username'] == username) & (df['role'] == role)].empty:
            return False  # Username is not unique
    return True  # Username is unique

# Function to handle user registration
def register_user(file_path):
    # Prompt user to enter username and password
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Display available roles for the user to select
    print("\nAvailable roles:")
    print("1. Patient")  
    print("2. Doctor")
    print("3. Mental Health Worker")
    print("4. Admin")
    role_choice = input("\nSelect role (1-4): ").strip()

    # Mapping role choices to their corresponding role strings
    roles = {
        "1": "patient",
        "2": "doctor",
        "3": "mhw",  # Mental Health Worker
        "4": "admin"
    }

    # Validate the role choice
    if role_choice not in roles:
        print("Invalid role selection.")
        return

    role = roles[role_choice]  # Get the corresponding role string

    # Ensure username and password are not empty
    if not username or not password:
        print("Username and password cannot be empty.")
        return

    # For special roles, require a verification code
    if role in ["admin", "doctor", "mhw"]:
        verification_code = input(f"Enter {role} registration code: ").strip()
        # Verify the code (currently set to "0000" for all roles)
        if verification_code != "0000":
            print(f"Invalid {role} code. Registration failed.")
            return

    # Check if the username is unique for the selected role
    if not is_username_unique(username, role, file_path):
        print(f"Username '{username}' already exists for role '{role}'.")
        return

    # Create a new user instance and save it to the CSV file
    new_user = User(username, password, role)
    new_user.save_to_csv(file_path)
    print("Registration successful!")
