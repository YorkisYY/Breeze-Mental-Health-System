import pandas as pd
from model.user import User  
from model.admin import handle_admin_menu
from model.doctor import handle_doctor_menu
from model.mhwp import handle_mhw_menu
from model.patient import handle_patient_menu

def login_user(file_path):
   """Authenticate and login user.
   Args:
       file_path: Path to user data CSV file
   Returns:
       User object if login successful, None otherwise
   """
   username = input("Enter username: ").strip()
   password = input("Enter password: ").strip()
   
   # Create user object with temporary role
   user = User(username, password, "temp")
   
   # Verify credentials
   if user.load_from_csv(file_path):
       hashed_password = user.hash_password(password) 
       if user.password == hashed_password:
           print(f"Login successful! Welcome, {user.username}!")
           return user
       else:
           print("Incorrect password.")
   else:
       print("User does not exist.")
   return None

def verify_staff(role):
    """Verify staff members with role-specific code"""
    verification_code = input(f"Enter {role} verification code: ")
    if verification_code == "0000":
        print("Verification successful!")
        return True
    else:
        print("Verification failed. Access denied.")
        return False

def handle_login(file_path):
    user = login_user(file_path)
    if user:
        print(f"Login successful! You are logged in as {user.role}.")
        match user.role:
            case "admin":
                if not verify_staff("admin"):
                    return False
                handle_admin_menu(user, file_path)
            case "doctor":
                if not verify_staff("doctor"):
                    return False
                handle_doctor_menu(user, file_path)
            case "mhw":
                if not verify_staff("mhw"):
                    return False
                handle_mhw_menu(user, file_path)
            case "patient":
                handle_patient_menu(user, file_path)
    return True

    