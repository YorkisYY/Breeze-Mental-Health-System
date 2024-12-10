import pandas as pd
from config import *

def handle_account_management(user):
    while True:
        print("\nAccount Management:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. Change Email")
        print("4. Change Emergency Email")
        print("5. Delete Account")
        print("6. Back to Main Menu")

        account_choice = input("Select an option (1-6): ").strip()

        if account_choice == '1':
            try:
                new_username = input("Enter new username: ").strip()
                if not new_username:
                    print("Username cannot be empty.")
                    continue
                user_df = pd.read_csv(USER_DATA_PATH)
                if new_username in user_df[user_df['username'] != user.username]['username'].values:
                    print("Username already exists. Please choose a different one.")
                    continue

                if user.update_info(new_username=new_username):
                    continue
                else:
                    print("Failed to update username. Please try again.")
            except Exception as e:
                print(f"Error updating username: {str(e)}")

        elif account_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)

        elif account_choice == '3':
            new_email = input("Enter new email: ").strip()
            if user.update_info(new_email=new_email):  
                print("Email updated successfully!")
            else:
                print("Failed to update email. Try again.")

        elif account_choice == '4':
            new_emergency_email = input("Enter new emergency email: ").strip()
            if user.update_info(new_emergency_email=new_emergency_email):
                continue
            else:
                print("Failed to update emergency email. Try again.")

        elif account_choice == '5':
            confirm = input("Confirm delete account? (yes/no): ").strip()
            if confirm.lower() == "yes":
                user.delete_from_csv()
                print("Account deleted successfully.")
                return True
        elif account_choice == '6':
            break
        else:
            print("Invalid choice, please try again.")
    return False