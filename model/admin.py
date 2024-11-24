def handle_admin_menu(user, file_path):
    while True:
        print("\nAdmin Options:")
        print("1. Update Another User's Info")
        print("2. Delete Another User")
        print("3. View System Statistics")
        print("4. View all the appointment")
        print("4. Logout")

        admin_choice = input("Select an option (1-4): ")
        if admin_choice == '1':
            target_username = input("Enter the username to update: ")
            new_username = input("Enter the new username (blank to keep): ").strip()
            new_password = input("Enter the new password (blank to keep): ").strip()
            user.admin_update_user(file_path, target_username, new_username or None, new_password or None)
        elif admin_choice == '2':
            target_username = input("Enter the username to delete: ")
            user.admin_delete_user(file_path, target_username)
        elif admin_choice == '3':
            print("System statistics feature coming soon...")
        elif admin_choice == '5':  # View all appointments
            user.view_appointments("data/appointments.csv")

        elif admin_choice == '5':
            print("Logging out of admin session.")
            break
        else:
            print("Invalid choice, please try again.")
