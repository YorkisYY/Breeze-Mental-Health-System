def handle_doctor_menu(user):
    '''Handle the doctor related pages
    
    '''
    # # import doctor related data file path.
    # from config import OTHER_DATA_PATH
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