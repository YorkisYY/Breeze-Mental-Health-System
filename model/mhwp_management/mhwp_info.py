import pandas as pd
from config import *

def handle_update_personal_info(user):
    while True:
        print("\nUpdate Personal Information Options:")
        print("1. Update username")
        print("2. Change password")
        print("3. Change email")
        print("4. Change emergency email")
        print("5. Delete account")
        print("6. Back to main menu")

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
                return False
        elif info_choice == '6':
            break
        else:
            print("Invalid input. Please try.")