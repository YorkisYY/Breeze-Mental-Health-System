import os
import pandas as pd
from model.user import User  # Ensure this path matches your project structure

FILE_PATH = "user_data.csv"

# Initialize CSV file if it doesn't exist
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, 'w') as f:
        f.write("username,password,role\n")

def register_user():
    """Register a new user"""
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
    
    new_user = User(username, password, role)
    
    # Check if username is unique
    if new_user.load_from_csv(FILE_PATH):
        print("Username has been used. Please choose a different one.")
        return
    
    # Save user information to CSV file
    new_user.save_to_csv(FILE_PATH)
    print("Registration successful!")

def login_user():
    """User login"""
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    user = User(username, password)
    if user.load_from_csv(FILE_PATH):
        # Verify password
        if user.password == user.hash_password(password):
            print(f"Login successful! Welcome, {user.username}!")
            return user
        else:
            print("Incorrect password.")
    else:
        print("User does not exist.")
    return None

def main():
    print("Welcome to the User Management System")
    while True:
        print("\nChoose an option:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select an option (1/2/3): ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            user = login_user()
            if user:
                print(f"You are logged in as {user.role}.")
                # Additional role-based actions can be added here, e.g., admin user management
                if user.role == "admin":
                    print("Admin privileges granted. (Further admin options can be added here.)")
        elif choice == '3':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
