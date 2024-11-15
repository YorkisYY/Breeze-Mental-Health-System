import os
import pandas as pd
from model.user import User

FILE_PATH = "user_data.csv"

# Initialize CSV file if it doesn't exist
def initialize_csv(file_path):
    """Initialize the CSV file if it doesn't exist."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("username,password,role\n")

def is_username_unique(username, role, file_path):
    """Check if the username already exists with the specified role in the CSV file."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Check if there is a user with the same username and role
        if not df[(df['username'] == username) & (df['role'] == role)].empty:
            return False
    return True

def register_user(file_path):
    """Register a new user, with an extra check for admin registration."""
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    role = input("Enter role (user/admin): ").strip().lower()
    
    # Check for empty inputs and valid role
    if not username:
        print("Username cannot be empty.")
        return
    if not password:
        print("Password cannot be empty.")
        return
    if role not in ["user", "admin"]:
        print("Invalid role. Please enter 'user' or 'admin'.")
        return

    # Admin registration requires the admin code
    if role == "admin":
        admin_code = input("Enter admin registration code: ").strip()
        if admin_code != "0000":
            print("Invalid admin code. Admin registration failed.")
            return
    
    # Check if username is unique for the given role
    if not is_username_unique(username, role, file_path):
        print(f"The username '{username}' is already used for role '{role}'. Please choose a different one.")
        return
    
    # Create and save the new user
    new_user = User(username, password, role)
    new_user.save_to_csv(file_path)
    print("Registration successful!")
