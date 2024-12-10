import os
import csv
from tabulate import tabulate
import random
from config import *
from model.user_account_management.user_data_manage import toggle_user_account_status
import pandas as pd
from utils.list_all_user import list_all_users
from services.summary import display_summary
from .admin_management import *

def handle_admin_menu(user):
    """
    Admin menu to manage assignments, view unassigned users, and modify user data.
    """
    while True:
        print("\nAdmin Options:")
        print("1. Update Another User's Info")
        print("2. Delete Another User")
        print("3. View System Statistics")
        print("4. View All Assignments")
        print("5. Assign Patients to MHWPs")
        print("6. Modify Assignments")
        print("7. Display Unassigned Patients and MHWPs")
        print("8. Enable/Disable User Account") # @Arthur: 2024_12_03 add user account status management
        print("9. Logout")

        
        admin_choice = input("Select an option (1-9): ").strip()

        if admin_choice == '1':  # Update another user's info
            target_username = input("Enter the username to update: ").strip()
            new_username = input("Enter the new username (blank to keep): ").strip()
            new_password = input("Enter the new password (blank to keep): ").strip()
            new_email = input("Enter the new email (blank to keep): ").strip()
            new_emergency_email = input("Enter the new emergency email (blank to keep): ").strip()

            user.admin_update_user(
                target_username,
                new_username or None,
                new_password or None,
                new_email or None,
                new_emergency_email or None
            )

        elif admin_choice == '2':
            target_username = input("Enter the username to delete: ").strip()
            result = user.admin_delete_user(target_username)
            if result == "self_deleted":
                return 
        elif admin_choice == '3':  # View system statistics
            display_summary()

        elif admin_choice == '4':  # View all assignments
            print("\n--- All Assignments ---")
            display_assignments(ASSIGNMENTS_DATA_PATH, USER_DATA_PATH)

        elif admin_choice == '5':  # Assign patients to MHWPs
            print("\n--- Assigning Patients to MHWPs ---")
            balanced_assign_patients_and_mhwps(
                patient_data_path=PATIENTS_DATA_PATH,
                mhwp_data_path=MHWP_DATA_PATH, 
                assignments_path=ASSIGNMENTS_DATA_PATH,
                schedule_path=SCHEDULE_DATA_PATH
            )

        elif admin_choice == '6':  # Modify Assignments
            print("\n--- Modify Assignments ---")
            modify_assignments()

        elif admin_choice == '7':  # Display unassigned users
            print("\n--- Unassigned Patients and MHWPs ---")
            display_unassigned_users(
                patient_data_path=PATIENTS_DATA_PATH,
                mhwp_data_path=MHWP_DATA_PATH,
                assignments_path=ASSIGNMENTS_DATA_PATH
            )
 
        elif admin_choice == '8':  # Manage user account status
            print("\n--- Manage User Account Status ---")
            print("Select user type to modify:")
            print("1. MHWP")
            print("2. Patient")
            
            role_choice = input("Enter choice (1-2): ").strip()
            if role_choice == '1':
                selected_username = list_all_users('mhwp')
            elif role_choice == '2':
                selected_username = list_all_users('patient')
            else:
                print("Invalid choice")
                continue

            if selected_username:
                success, message = toggle_user_account_status(selected_username)
                print(message)
            else:
                print("Operation cancelled")
                
        elif admin_choice == '9':  # Logout
            print("Logging out of admin session.")
            break


        else:
            print("Invalid choice. Please select a valid option.")
            return True
