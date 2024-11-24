from services.registration import register_user, initialize_csv
from services.login import handle_login
import os
from utils.display_banner import display_banner


# data directory and Initialize CSV file if it doesn't exist
FILE_PATH = "data\\patient_data.csv"
MOOD_DATA_PATH = "data\\mood_data.csv"
initialize_csv(FILE_PATH)

def handle_exit():
    print("Exiting the system now.")
    return True

def handle_invalid():
    print("Invalid choice, please try again.")
    return False

def main():
    # Display welcome banner with original ASCII art 
    display_banner()
    
    while True:
        # Main menu options
        print("\nChoose an option:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option (1/2/3): ")
        
        menu_actions = {
            '1': lambda: register_user(FILE_PATH) or False,
            '2': lambda: handle_login(FILE_PATH),
            '3': lambda: handle_exit(),
            }
        #@mikrostiff: ")()" is not a tyoo
        result = menu_actions.get(choice, handle_invalid)() 
        
        
if __name__ == "__main__":
   main()
   