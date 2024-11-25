def handle_mhw_menu(user):
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