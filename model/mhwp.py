import csv
from os.path import exists
from notification import send_email_notification, get_email_by_username

def list_appointments_for_mhw(mhw_username, file_path):
    """List appointments for the currently logged-in MHW"""
    appointments = []
    
    # Check if file exists
    if not exists(file_path):
        print(f"Error: Appointment record file '{file_path}' not found")
        return appointments

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # First read all matching appointments
            for row in reader:
                if row['mhwp_username'] == mhw_username:
                    appointments.append(row)
            
            # Check if any appointments were found
            if not appointments:
                print(f"\nNo appointments found for {mhw_username}")
                return appointments
            
            # Only print table if records exist
            print("\nAppointments for MHW:", mhw_username)
            print("------------------------------------------------------------------")
            print("ID | Patient      | Date       | Start  | End    | Status")
            print("------------------------------------------------------------------")
            for idx, row in enumerate(appointments, start=1):
                print(f"{idx:2d} | {row['patient_username']:<10} | {row['date']} | {row['start_time']} | {row['end_time']} | {row['status']}")
            
    except Exception as e:
        print(f"Error reading appointments: {str(e)}")
    
    return appointments

def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. View Patient Records")
        print("2. Add Counseling Notes")
        print("3. Manage Appointments")
        print("4. Logout")

        mhwp_choice = input("Select an option (1-4): ").strip()
        
        if mhwp_choice == '1':  # View Patient Records
            print("This feature is coming soon...")

        elif mhwp_choice == '2':  # Add Counseling Notes
            print("This feature is coming soon...")

        elif mhwp_choice == '3':  # Manage Appointments
            while True:
                print("\nManage Appointments:")
                print("1. View all appointments")
                print("2. Confirm an appointment")
                print("3. Cancel an appointment") 
                print("4. Back to main menu")

                manage_choice = input("Select an option (1-4): ").strip()

                if manage_choice == "1":  # View all appointments
                    appointments = list_appointments_for_mhw(user.username, "data/appointments.csv")
                    if not appointments:
                        continue  # Return to appointment management menu
                
                elif manage_choice in ["2", "3"]:  # Confirm or cancel an appointment
                    # List all appointments for current worker
                    appointments = list_appointments_for_mhw(user.username, "data/appointments.csv")
                    if not appointments:
                        continue  # Return to appointment management menu
                    
                    # Ask user to select an appointment
                    appointment_id = input("Enter the ID of the appointment to manage: ").strip()
                    try:
                        appointment_id = int(appointment_id) - 1
                        if 0 <= appointment_id < len(appointments):
                            selected_appointment = appointments[appointment_id]
                            action = "confirm" if manage_choice == "2" else "cancel"
                            try:
                                user.manage_appointments(
                                    "data/appointments.csv",
                                    action,
                                    selected_appointment['patient_username'],
                                    selected_appointment['date'],
                                    selected_appointment['start_time']
                                )
                                print(f"Appointment successfully {action}ed!")
                                # Send email notification
                                patient_email = get_email_by_username(selected_appointment['patient_username'])
                                if patient_email:
                                    subject = f"Your appointment has been {action}ed"
                                    message = (
                                        f"Dear {selected_appointment['patient_username']},\n\n"
                                        f"Your appointment with {user.username} on {selected_appointment['date']} "
                                        f"at {selected_appointment['start_time']} has been {action}ed.\n\n"
                                        "Regards,\nMental Health Support System"
                                    )
                                    send_email_notification(patient_email, subject, message)
                                    print(f"Notification email sent to {selected_appointment['patient_username']}.")
                                else:
                                    print("Error: Could not retrieve patient's email address.")
                            except Exception as e:
                                print(f"Error processing appointment: {str(e)}")
                        else:
                            print("Invalid ID. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a valid appointment ID.")
                
                elif manage_choice == "4":  # Back to MHW Options
                    print("Returning to main menu...")
                    break
                
                else:
                    print("Invalid choice, please select an option between 1 and 4.")

        elif mhwp_choice == '4':  # Logout
            print("Logout successful. Goodbye!")
            break
        
        else:
            print("Invalid choice, please select an option between 1 and 4.")