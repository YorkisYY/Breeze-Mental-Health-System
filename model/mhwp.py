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
from .mhwp_management import *


def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. Update Personal Information")
        print("2. Set your schedule")
        print("3. Manage appointments")
        print("4. View patient records")
        print("5. View your dashboard")
        print("6. Logout")

        main_choice = input("Select an option (1-6): ").strip()
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
            display_dashboard(user.username)

        elif main_choice == '6':  # Logout
            break

        else:
            print("Invalid choice. Please select an option between 1 and 6.")
