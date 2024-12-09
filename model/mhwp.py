import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
from config import *
from services.comment import view_comments
from services.patient_records import view_patient_records
from utils.notification import send_email_notification, get_email_by_username
from services.dashboard import display_dashboard
from .mhwp_management.mhwp_schedule import *

def handle_update_personal_info(user):
    print("\nUpdate Personal Information Options:")
    print("1. Update username")
    print("2. Change password")
    print("3. Change email")
    print("4. Change emergency email")
    print("5. Delete account")

    info_choice = input("Select an option (1-5): ").strip()

    if info_choice == '1':  # Update username
        try:
            new_username = input("Enter new username: ").strip()
            if not new_username:
                print("Username cannot be empty.")
                return

            user_df = pd.read_csv(USER_DATA_PATH)
            if new_username in user_df['username'].values:
                print("Username already exists. Please choose a different one.")
                return

            if user.update_info(new_username=new_username):
                return
            else:
                print("Failed to update username. Please try again.")
        except Exception as e:
            print(f"Error updating username: {str(e)}")

    elif info_choice == '2':  # Change password
        new_password = input("Enter new password: ").strip()
        if user.update_info(new_password=new_password):
            print("Password updated successfully!")
        else:
            print("Failed to update password. Try again.")

    elif info_choice == '3':  # Change email
        new_email = input("Enter new email: ").strip()
        if not new_email:
            print("Email cannot be empty. Please try again.")
            return
        if user.update_info(new_email=new_email):
            print("Email updated successfully!")
        else:
            print("Failed to update email. Try again.")

    elif info_choice == '4':  # Change emergency email
        new_emergency_email = input("Enter new emergency email: ").strip()
        if not new_emergency_email:
            print("Emergency email cannot be empty. Please try again.")
            return
        if user.update_info(new_emergency_email=new_emergency_email):
            print("Emergency email updated successfully!")
        else:
            print("Failed to update emergency email. Try again.")

    elif info_choice == '5':  # Delete account
        confirm = input("Confirm delete account? (yes/no): ").strip()
        if confirm.lower() == "yes":
            user.delete_from_csv()
            print("Account deleted successfully.")
            return True
    return False


def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. Update Personal Information")
        print("2. Set your schedule")
        print("3. Manage appointments")
        print("4. View patient records")
        print("5. Logout")

        main_choice = input("Select an option (1-5): ").strip()
        if main_choice == '1':
            if handle_update_personal_info(user):  # If account is deleted
                return

        elif main_choice == '2':
            handle_set_schedule(user)

        elif main_choice == '3':
            handle_manage_appointments(user)

        elif main_choice == '4':
            try:
                print("\nViewing patient records...")
                view_patient_records(user.username)
            except Exception as e:
                print(f"Error viewing patient records: {str(e)}")

        elif main_choice == '5':  # Logout
            break

        else:
            print("Invalid choice. Please select an option between 1 and 5.")
