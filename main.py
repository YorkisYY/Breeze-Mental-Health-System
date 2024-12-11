from services.registration import register_user
from services.login import handle_login
import os
import sys
import shutil
from utils.display_banner import display_banner
from services import *
from model import *
from config import *
from model.mhwp_management.mhwp_schedule import *

def initialize_data_directory():
    """Create data directory and extract initial CSV files if needed"""
    # Define data directory relative to executable
    if getattr(sys, 'frozen', False):
        app_dir = sys._MEIPASS
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else app_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Copy initial CSV files if they don't exist
    for csv_file in ['user_data.csv', 'mhwp.csv', 'patients.csv', 'assignments.csv', 
                     'mhwp_schedule.csv', 'mhwp_schedule_template.csv', 
                     'meditation_resources.csv']:
        target_file = os.path.join(data_dir, csv_file)
        if not os.path.exists(target_file):
            source_file = os.path.join(app_dir, 'data', csv_file)
            if os.path.exists(source_file):
                shutil.copy2(source_file, target_file)
    
    return data_dir

def handle_exit():
    print("Exiting the system now.")
    return False

def handle_invalid():
    print("Invalid choice, please try again.")
    return True

def show_menu():
    print("\nChoose an option:")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return input("Select an option (1/2/3): ")

def main():
    # Initialize data directory first
    data_dir = initialize_data_directory()
    
    # Update config paths if needed
    if data_dir != DATA_DIR:
        print(f"Using data directory: {data_dir}")
    
    update_mhwp_schedules(silent=True)
    display_banner()
    choice = show_menu()
    
    menu_actions = {
        '1': lambda: register_user(),
        '2': lambda: handle_login(),
        '3': lambda: handle_exit(),
    }

    while menu_actions.get(choice, handle_invalid)():
        choice = show_menu()

 
if __name__ == "__main__":
    main()
   