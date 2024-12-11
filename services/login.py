# handles all login related function and user interface 

import pandas as pd
import getpass
from model.user_account_management.user import User  
from model.admin import handle_admin_menu
from model.mhwp import handle_mhwp_menu
from model.patient import handle_patient_menu
from config import *

def login_user():
   """Authenticate and login user.
   Args:
       file_path: Path to user data CSV file
   Returns:
       User object if login successful, None otherwise
   """
   username = input("Enter username: ").strip()
   password = getpass.getpass("Enter password: ").strip()
   
   # Create user object with temporary role
   user = User(username, password, "temp")
   
   # Verify credentials
   if user.load_from_csv():
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
    verification_code = getpass.getpass(f"Enter {role} verification code: ").strip()
    if verification_code == "0000":
        print("Verification successful!")
        return True
    else:
        print("Verification failed. Access denied.")
        return False

def handle_login():
    user = login_user()
    if user:
        # Check user status from respective CSV files based on role
        if user.role == "mhwp":
            df = pd.read_csv(MHWP_DATA_PATH) # read mhwp data from config
            status = df[df['username'] == user.username]['account_status'].values[0]
            if status == 'inactive':
                print("Your account is disabled. Please contact admin to reactivate.")
                return True  
        elif user.role == "patient":
            df = pd.read_csv(PATIENTS_DATA_PATH) # read patients data from config
            status = df[df['username'] == user.username]['account_status'].values[0]
            if status == 'inactive':
                print("Your account is disabled. Please contact admin to reactivate.")
                return True  

        print(f"You are logged in as {user.role}.")
        match user.role:
            case "admin":
                if not verify_staff("admin"):
                    return False
                handle_admin_menu(user)
            case "mhwp":
                if not verify_staff("mhwp"):
                    return False
                handle_mhwp_menu(user)
            case "patient":
                handle_patient_menu(user)
    return True
    