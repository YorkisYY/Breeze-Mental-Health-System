import csv
from os.path import exists

from datetime import datetime, timedelta
import calendar
from services.comment import view_comments_for_mhwp
from services.patient_records import view_patient_records
from utils.notification import send_email_notification, get_email_by_username

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


def generate_schedule(username, weekdays, time_range, output_file):
    """
    Generate a 3-month schedule based on user availability and save it to a CSV file.

    :param username: Username of the MHW
    :param weekdays: List of weekdays (e.g., ["Monday", "Tuesday"])
    :param time_range: Dictionary with start and end time (e.g., {"start": "14:00", "end": "16:00"})
    :param output_file: Path to the output CSV file
    """
    # Start from today
    today = datetime.today()
    end_date = today + timedelta(days=90)  # 3 months later

    # Get numerical representations of weekdays
    weekday_map = {day: idx for idx, day in enumerate(calendar.day_name)}
    selected_weekdays = [weekday_map[day] for day in weekdays]

    # Convert time range to datetime.time
    start_time = datetime.strptime(time_range['start'], "%H:%M").time()
    end_time = datetime.strptime(time_range['end'], "%H:%M").time()

    # Generate dates
    schedule = []
    current_date = today
    while current_date <= end_date:
        if current_date.weekday() in selected_weekdays:
            schedule.append({
                "mhwp_username": username,
                "date": current_date.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M")
            })
        current_date += timedelta(days=1)

    # Save to CSV
    with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = ["mhwp_username", "date", "start_time", "end_time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(schedule)

    print(f"Schedule generated and saved to {output_file}.")


def display_current_schedule(username, file_path):
    """Display the current open schedule for the MHW"""
    if not exists(file_path):
        print(f"Error: Schedule file '{file_path}' not found.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            schedule = [row for row in reader if row['mhwp_username'] == username]

            if not schedule:
                print("\nNo available schedule found for your account.")
                return

            print(f"\nCurrent Open Schedule for {username}:")
            print("------------------------------------------------------------------")
            print("Date       | Start Time | End Time")
            print("------------------------------------------------------------------")
            for row in schedule:
                print(f"{row['date']} | {row['start_time']}   | {row['end_time']}")
            print("------------------------------------------------------------------")

    except Exception as e:
        print(f"Error displaying schedule: {str(e)}")


def setup_mhwp_schedule(user):
    """Set up availability schedule for the Mental Health Worker."""
    print("\nSetup Your Availability")
    weekdays = input("Enter available weekdays (e.g., Monday, Tuesday): ").split(",")
    weekdays = [day.strip().capitalize() for day in weekdays]

    start_time = input("Enter start time (HH:MM, 24-hour format): ").strip()
    end_time = input("Enter end time (HH:MM, 24-hour format): ").strip()

    output_file = "data/mhwp_schedule.csv"
    generate_schedule(
        username=user.username,
        weekdays=weekdays,
        time_range={"start": start_time, "end": end_time},
        output_file=output_file
    )

    print(f"Your schedule has been successfully created for the next 3 months.")


def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. View Patient Records")
        print("2. Add Counseling Notes")
        print("3. Manage Appointments")
        print("4. Set Up Your Availability")
        print("5. View Your Current Schedule")
        print("6. View comments from your patients")
        print("7. Logout")

        mhwp_choice = input("Select an option (1-6): ").strip()
        
        if mhwp_choice == '1':  # View Patient Records
            view_patient_records(user.username)

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
                    appointments = list_appointments_for_mhw(user.username, "data/appointments.csv")
                    if not appointments:
                        continue  # Return to appointment management menu
                    
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

        elif mhwp_choice == '4':  # Set up availability
            setup_mhwp_schedule(user)

        elif mhwp_choice == '5':  # View current schedule
            display_current_schedule(user.username, "data/mhwp_schedule.csv")

        elif mhwp_choice == '6':  # 查看评论
            view_comments_for_mhwp(user)

        elif mhwp_choice == '7':  # Logout
            print("Logout successful. Goodbye!")
            break
        
        else:
            print("Invalid choice, please select an option between 1 and 6.")
