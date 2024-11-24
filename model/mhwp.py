def handle_mhw_menu(user, file_path):
    while True:
        print("\nMental Health Worker Options:")
        print("1. View Patient Records")
        print("2. Add Counseling Notes")
        print("3. Manage Appointments")
        print("4. Logout")
        
        if mhwp_choice == '3':  # Manage appointments
            print("\nManage Appointments:")
            print("1. View all appointments")
            print("2. Confirm an appointment")
            print("3. Cancel an appointment")

            manage_choice = input("Select an option (1-3): ").strip()

            if manage_choice == "1":
                user.manage_appointments("data/appointments.csv", "view")
            elif manage_choice in ["2", "3"]:
                patient_username = input("Enter patient's username: ").strip()
                date = input("Enter appointment date (YYYY-MM-DD): ").strip()
                start_time = input("Enter appointment start time (HH:MM): ").strip()
                action = "confirm" if manage_choice == "2" else "cancel"
                user.manage_appointments("data/appointments.csv", action, patient_username, date, start_time)
            else:
                print("Invalid choice.")



        mhw_choice = input("Select an option (1-4): ")
        if mhw_choice == '4':
            print("Logging out of MHW session.")
            break
        else:
            print("This feature is coming soon...")
       