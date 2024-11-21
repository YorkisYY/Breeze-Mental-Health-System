from model.registration import register_user, initialize_csv
from model.login import login_user
import os

FILE_PATH = "patient_data.csv"

# Initialize CSV file if it doesn't exist
initialize_csv(FILE_PATH)

def verify_staff(role):
   """Verify staff members with role-specific code"""
   verification_code = input(f"Enter {role} verification code: ")
   if verification_code == "0000":
       print("Verification successful!")
       return True
   else:
       print("Verification failed. Access denied.")
       return False

def main():
   # Display welcome banner with original ASCII art 
   print("=" * 60)
   print("            ██   ██ ███████ ██      ██       ██████   ")
   print("            ██   ██ ██      ██      ██      ██    ██   ")
   print("            ███████ █████   ██      ██      ██    ██   ")
   print("            ██   ██ ██      ██      ██      ██    ██   ")
   print("            ██   ██ ███████ ███████ ███████  ██████    ")
   print("            🌞🌞🌞  Welcome to                   🌞🌞🌞")
   print("            🌞🌞🌞  Breeze Mental Health System  🌞🌞🌞")  
   print("=" * 60)

   while True:
       # Main menu options
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
               
               # Route to appropriate menu based on role
               if user.role == "admin":
                   if not verify_staff("admin"):
                       continue

                   # Admin functions menu
                   while True:
                       print("\nAdmin Options:")
                       print("1. Update Another User's Info")
                       print("2. Delete Another User") 
                       print("3. View System Statistics")
                       print("4. Logout")

                       admin_choice = input("Select an option (1-4): ")
                       if admin_choice == '1':
                           target_username = input("Enter the username to update: ")
                           new_username = input("Enter the new username (blank to keep): ").strip()
                           new_password = input("Enter the new password (blank to keep): ").strip()
                           user.admin_update_user(FILE_PATH, target_username, new_username or None, new_password or None)
                       elif admin_choice == '2':
                           target_username = input("Enter the username to delete: ")
                           user.admin_delete_user(FILE_PATH, target_username)  
                       elif admin_choice == '3':
                           print("System statistics feature coming soon...")
                       elif admin_choice == '4':
                           print("Logging out of admin session.")
                           break
                       else:
                           print("Invalid choice, please try again.")

               elif user.role == "doctor":
                   if not verify_staff("doctor"):
                       continue
                       
                   # Doctor functions menu
                   while True:
                       print("\nDoctor Options:")
                       print("1. View Patient Records")
                       print("2. Add Diagnosis")
                       print("3. Manage Appointments")
                       print("4. Logout")
                       
                       doctor_choice = input("Select an option (1-4): ")
                       if doctor_choice == '4':
                           print("Logging out of doctor session.")
                           break  
                       else:
                           print("This feature is coming soon...")

               elif user.role == "mhw":
                   if not verify_staff("mhw"):
                       continue
                       
                   # Mental Health Worker functions menu
                   while True:
                       print("\nMental Health Worker Options:") 
                       print("1. View Patient Records")
                       print("2. Add Counseling Notes")
                       print("3. Manage Appointments")
                       print("4. Logout")
                       
                       mhw_choice = input("Select an option (1-4): ")
                       if mhw_choice == '4':
                           print("Logging out of MHW session.")
                           break
                       else:
                           print("This feature is coming soon...")

               else:  # Patient menu  
                   while True:
                       print("\nPatient Options:")
                       print("1. Update Personal Info")
                       print("2. Change Password")
                       print("3. View Medical Records") 
                       print("4. Book Appointment")
                       print("5. Delete Account")
                       print("6. Logout")

                       patient_choice = input("Select an option (1-6): ")
                       if patient_choice == '1':
                           new_username = input("Enter new username: ").strip()
                           user.update_info(FILE_PATH, new_username=new_username)
                       elif patient_choice == '2':
                           new_password = input("Enter new password: ").strip()
                           user.update_password(FILE_PATH, new_password)
                       elif patient_choice == '3':
                           print("Medical records feature coming soon...")
                       elif patient_choice == '4':
                           print("Appointment booking feature coming soon...")    
                       elif patient_choice == '5':
                           confirm = input("Confirm delete account? (yes/no): ")
                           if confirm.lower() == "yes":
                               user.delete_from_csv(FILE_PATH)
                               print("Account deleted successfully.")
                               break
                       elif patient_choice == '6':
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