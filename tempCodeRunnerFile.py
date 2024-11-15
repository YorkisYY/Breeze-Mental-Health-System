from model.registration import register_user, initialize_csv
from model.login import login_user
import os
from model.user import User

FILE_PATH = "user_data.csv"

# Initialize CSV file if it doesn't exist
initialize_csv(FILE_PATH)

def admin_verification():
    """Secondary verification for admin with a password check"""
    verification_code = input("Enter admin verification code: ")
    if verification_code == "0000":
        print("Verification successful!")
        return True
    else:
        print("Verification failed. Access denied.")
        return False

def main():
    print("=" * 60)
    print("            ██   ██ ███████ ██      ██       ██████   ")
    print("            ██   ██ ██      ██      ██      ██    ██   ")
    print("            ███████ █████   ██      ██      ██    ██   ")
    print("            ██   ██ ██      ██      ██      ██    ██   ")
    print("            ██   ██ ███████ ███████ ███████  ██████    ")
    print("            🌞🌞🌞   Welcome to    🌞🌞🌞")
    print("            🌞🌞🌞  Breeze Mental Health System  🌞🌞🌞")
    print("=" * 60)

    while True:
        print("\nChoose an option:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select an option (1/2/3): ")
        
        if choice == '1':
            register_user(FILE_PATH)
        elif choice == '2':
            user = login_user(FILE_PATH)
            if user:
                print(f"Login successful! You are logged in as {user.role}.")
                
                # Admin verification check
                if user.role == "admin":
                    if not admin_verification():
                        continue  # Go back to main menu if verification fails

                    # Admin actions
                    while True:
                        print("\nAdmin Options:")
                        print("1. Update Another User's Info")
                        print("2. Delete Another User")
                        print("3. Logout")
                        print("For deleting a user, please read the csv file to make sure the username:")

                        admin_choice = input("Select an option (1/2/3): ")
                        if admin_choice == '1':
                            target_username = input("Enter the username to update: ")
                            new_username = input("Enter the new username (leave blank to keep current): ").strip()
                            new_password = input("Enter the new password (leave blank to keep current): ").strip()
                            user.admin_update_user(FILE_PATH, target_username, new_username or None, new_password or None)
                        elif admin_choice == '2':
                            target_username = input("Enter the username to delete: ")
                            user.admin_delete_user(FILE_PATH, target_username)
                        elif admin_choice == '3':
                            print("Logging out of admin session.")
                            break
                        else:
                            print("Invalid choice, please try again.")

                # Regular user actions
                else:
                    while True:
                        print("\nLogged-in Options:")
                        print("1. Update Username")
                        print("2. Update Password")
                        print("3. Delete Account")
                        print("4. Logout")

                        user_choice = input("Select an option (1/2/3/4): ")
                        if user_choice == '1':
                            new_username = input("Enter new username: ").strip()
                            user.update_info(FILE_PATH, new_username=new_username)
                        elif user_choice == '2':
                            new_password = input("Enter new password: ").strip()
                            user.update_info(FILE_PATH, new_password=new_password)
                        elif user_choice == '3':
                            confirm = input("Are you sure you want to delete your account? (yes/no): ")
                            if confirm.lower() == "yes":
                                user.delete_from_csv(FILE_PATH)
                                print("Account deleted successfully.")
                                break
                        elif user_choice == '4':
                            print("Logging out.")
                            break
                        else:
                            print("Invalid choice, please try again.")

            else:
                print("Login failed. Returning to main menu.")
        elif choice == '3':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
