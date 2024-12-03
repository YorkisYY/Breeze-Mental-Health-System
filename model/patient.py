import os
from services.mood_tracking import MoodEntry
from services.meditation import handle_search_meditation
from services.comment import comment,add_comment,get_available_appointments
from services.questionnaire import submit_questionnaire,remind_to_complete_questionnaire
from services.journaling import enter_journaling
from utils.notification import send_email_notification, get_email_by_username
import pandas as pd
from tabulate import tabulate  
def display_mhwp_schedule_for_patient(user, schedule_file, assignments_file):
    """
    Display the current schedule for the assigned MHW for the next month.
    Allows the patient to select a date by its real-time ID.
    """
    try:
        # Retrieve the assigned MHW for the patient
        assignments = pd.read_csv(assignments_file, header=None, names=["patient_username", "mhwp_username"])
        mhwp_record = assignments[assignments['patient_username'] == user.username]
        if mhwp_record.empty:
            print(f"No assigned MHW found for patient '{user.username}'.")
            return None
        mhwp_username = mhwp_record.iloc[0]['mhwp_username']

        # Load the schedule file
        if not os.path.exists(schedule_file):
            print(f"Error: Schedule file '{schedule_file}' not found.")
            return None

        schedule = pd.read_csv(schedule_file)
        mhwp_schedule = schedule[schedule['mhwp_username'] == mhwp_username]

        if mhwp_schedule.empty:
            print(f"No schedule found for MHW '{mhwp_username}'.")
            return None

        print(f"Your MHW '{mhwp_username}' schedule for the next month:")

        # Add real-time numbering for the rows
        mhwp_schedule = mhwp_schedule.reset_index(drop=True)
        mhwp_schedule.insert(0, "ID", mhwp_schedule.index + 1)

        # Remove the mhwp_username column for display
        mhwp_schedule = mhwp_schedule.drop(columns=["mhwp_username"])

        # Replace symbols with "Available" or "Unavailable" only for display purposes
        availability_columns = [
            "09:00-10:00 (0)", "10:00-11:00 (1)", "11:00-12:00 (2)",
            "12:00-13:00 (3)", "13:00-14:00 (4)", "14:00-15:00 (5)", "15:00-16:00 (6)"
        ]
        display_schedule = mhwp_schedule.copy()
        for col in availability_columns:
            if col in display_schedule.columns:
                display_schedule[col] = display_schedule[col].replace({"■": "Available", "□": "Unavailable", "●": "Unavailable", "▲": "Unavailable"})

        # Paginate schedule (10 rows per page)
        page_size = 10
        total_pages = (len(display_schedule) + page_size - 1) // page_size
        current_page = 1

        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = start_idx + page_size
            page_data = display_schedule.iloc[start_idx:end_idx]

            print(f"\nSchedule (Page {current_page}/{total_pages}):")
            print(tabulate(page_data, headers="keys", tablefmt="grid", showindex=False))

            # Pagination options
            print("\nOptions:")
            print("1. Next page")
            print("2. Previous page")
            print("3. Select a date by ID")
            print("4. Return to main menu")
            option = input("Select an option (1-4): ").strip()

            if option == "1" and current_page < total_pages:
                current_page += 1
            elif option == "2" and current_page > 1:
                current_page -= 1
            elif option == "3":
                date_id = input("Enter the ID of the date to select: ").strip()
                try:
                    date_id = int(date_id)
                    if 1 <= date_id <= len(mhwp_schedule):
                        selected_date = mhwp_schedule.iloc[date_id - 1]['Date']
                        print(f"You have selected the date: {selected_date}")
                        return selected_date
                    else:
                        print("Invalid ID. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid ID.")
            elif option == "4":
                print("Returning to main menu...")
                return None
            else:
                print("Invalid choice. Please select a valid option.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def display_available_time_slots(schedule_row):
    """
    Display available time slots for a given day in the schedule.
    """
    try:
        print(f"\nAvailable Time Slots for {schedule_row['Date']}:")
        time_slots = [
            "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00"
        ]
        available_slots = []

        for idx, slot in enumerate(time_slots):
            column_name = f"{slot} ({idx})"
            if column_name in schedule_row and schedule_row[column_name] == "■":
                available_slots.append((len(available_slots) + 1, slot))  # Use 1-based index for display

        if not available_slots:
            print("No available time slots.")
            return None

        # Display all available slots with user-friendly numbers
        for user_idx, slot in available_slots:
            print(f"{user_idx}. {slot}")

        return available_slots

    except KeyError as e:
        print(f"Error processing schedule row: Missing column {e}")
        return None
    except Exception as e:
        print(f"Error displaying available time slots: {e}")
        return None



def select_time_slot_and_book(user, date, mhwp_username, available_slots, schedule_file, assignments_file, appointment_file):
    """
    Allow the user to select a time slot and book the appointment.
    """
    try:
        slot_input = input("Enter the slot number to book: ").strip()
        try:
            user_selected_idx = int(slot_input)  # User-facing index (1-based)
            selected_slot = next((slot for user_idx, slot in available_slots if user_idx == user_selected_idx), None)

            if selected_slot:
                timeslot = selected_slot  # Retrieve the actual time slot
                if book_appointment(user, date, timeslot, schedule_file, assignments_file, appointment_file):
                    print("Appointment booked successfully!")

                    # Notify the MHW
                    mhwp_email = get_email_by_username(mhwp_username)
                    if mhwp_email:
                        subject = "New Appointment Booked"
                        message = (
                            f"Dear {mhwp_username},\n\n"
                            f"An appointment has been booked by {user.username} on {date} during {timeslot}.\n\n"
                            "Regards,\nBreeze Mental Health Support System"
                        )
                        send_email_notification(mhwp_email, subject, message)
                    else:
                        print("Error: Could not retrieve MHW's email address.")
                else:
                    print("Failed to book the appointment.")
            else:
                print("Invalid slot number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid slot number.")
    except Exception as e:
        print(f"Unexpected error: {e}")



def book_appointment_with_schedule(user, schedule_file, assignments_file, appointment_file):
    """
    Main function to book an appointment through schedule navigation.
    """
    try:
        selected_date = display_mhwp_schedule_for_patient(user, schedule_file, assignments_file)
        if selected_date is None:
            return  # User chose to return to the main menu

        # Retrieve the assigned MHW for the patient
        assignments = pd.read_csv(assignments_file, header=None, names=["patient_username", "mhwp_username"])
        mhwp_record = assignments[assignments['patient_username'] == user.username]
        if mhwp_record.empty:
            print(f"No assigned MHW found for patient '{user.username}'.")
            return
        mhwp_username = mhwp_record.iloc[0]['mhwp_username']

        # Load the MHW schedule for the selected date
        schedule = pd.read_csv(schedule_file)
        mhwp_schedule = schedule[
            (schedule['mhwp_username'] == mhwp_username) & (schedule['Date'] == selected_date)
        ]

        if mhwp_schedule.empty:
            print(f"No schedule found for MHW '{mhwp_username}' on {selected_date}.")
            return

        # Display available time slots for the selected date
        available_slots = display_available_time_slots(mhwp_schedule.iloc[0])
        if available_slots is None:
            return

        # Perform the booking
        select_time_slot_and_book(
            user, selected_date, mhwp_username, available_slots,
            schedule_file, assignments_file, appointment_file
        )

    except Exception as e:
        print(f"Unexpected error: {e}")



def book_appointment(user, date, timeslot, schedule_file, assignments_file, appointment_file):
    """
    Allow a patient to book an appointment with their assigned MHW.
    Updates mhwp_schedule.csv to mark the slot as booked (▲).
    """

    try:
        # Retrieve assigned MHW from assignments.csv
        try:
            assignments = pd.read_csv(assignments_file, header=None, names=["patient_username", "mhwp_username"])
            mhwp_record = assignments[assignments['patient_username'] == user.username]
            if mhwp_record.empty:
                print(f"No assigned MHW found for patient '{user.username}'.")
                return False
            mhwp_username = mhwp_record.iloc[0]['mhwp_username']
        except FileNotFoundError:
            print("Error: assignments.csv file not found.")
            return False

        # Check MHW's schedule in mhwp_schedule.csv
        try:
            schedule = pd.read_csv(schedule_file)
            mhwp_schedule = schedule[(schedule['mhwp_username'] == mhwp_username) & (schedule['Date'] == date)]

            if mhwp_schedule.empty:
                print(f"No schedule found for MHW '{mhwp_username}' on {date}.")
                return False

            # Find the correct time slot column in the schedule
            time_slot_column = [col for col in schedule.columns if timeslot in col]
            if not time_slot_column:
                print(f"Time slot '{timeslot}' is invalid.")
                return False
            time_slot_column = time_slot_column[0]

            # Check if the time slot is available (■)
            if not (mhwp_schedule[time_slot_column] == "■").any():
                print(f"The selected time slot '{timeslot}' is not available. Please choose another.")
                return False
        except FileNotFoundError:
            print("Error: mhwp_schedule.csv file not found.")
            return False

        # Check for conflicting appointments in appointments.csv
        try:
            appointments = pd.read_csv(appointment_file)
        except FileNotFoundError:
            appointments = pd.DataFrame(columns=['id', 'patient_username', 'mhwp_username', 'date', 'timeslot', 'status'])

        # Check for overlapping appointments
        overlapping_appointment = appointments[
            (appointments['mhwp_username'] == mhwp_username) &
            (appointments['date'] == date) &
            (appointments['timeslot'] == timeslot)
        ]
        if not overlapping_appointment.empty:
            print(f"The selected time slot '{timeslot}' overlaps with an existing appointment. Please choose another.")
            return False

        # Generate a sequential ID for the appointment
        if not appointments.empty:
            last_id = appointments['id'].max()  # Get the highest current ID
            appointment_id = last_id + 1
        else:
            appointment_id = 1

        # Record the new appointment in appointments.csv
        new_appointment = {
            "id": appointment_id,  # Add sequential ID
            "patient_username": user.username,
            "mhwp_username": mhwp_username,
            "date": date,
            "timeslot": timeslot,
            "status": "pending"
        }
        appointment_df = pd.DataFrame([new_appointment])
        try:
            appointment_df.to_csv(appointment_file, mode='a', header=not pd.read_csv(appointment_file).shape[0], index=False)
        except FileNotFoundError:
            appointment_df.to_csv(appointment_file, mode='w', header=True, index=False)

        # Update mhwp_schedule.csv to mark the slot as booked (▲)
        try:
            schedule.loc[
                (schedule['mhwp_username'] == mhwp_username) & (schedule['Date'] == date),
                time_slot_column
            ] = "▲"
            schedule.to_csv(schedule_file, index=False)
            print(f"Schedule updated: time slot '{timeslot}' is now booked.")
        except Exception as e:
            print(f"Error updating schedule: {e}")
            return False

       
        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def cancel_appointment_with_display(user, schedule_file, appointment_file):
    """
    Allow a patient to view and cancel their appointments.
    """
    try:
        # Load appointments for the patient
        appointments = pd.read_csv(appointment_file)
        user_appointments = appointments[appointments['patient_username'] == user.username]

        if user_appointments.empty:
            print("No appointments found to cancel.")
            return

        # Display appointment list
        print("\nYour current appointments:")
        user_appointments = user_appointments[['id', 'date', 'timeslot', 'status', 'mhwp_username']]
        print(tabulate(user_appointments, headers='keys', tablefmt='grid', showindex=False))

        # Enter the ID to cancel the appointment
        appointment_id = input("\nEnter the ID of the appointment to cancel: ").strip()
        try:
            appointment_id = int(appointment_id)
            if appointment_id not in user_appointments['id'].values:
                print("Invalid ID. Please try again.")
                return

            # Retrieve the selected appointment record
            selected_appointment = user_appointments[user_appointments['id'] == appointment_id].iloc[0]
            date = selected_appointment['date']
            timeslot = selected_appointment['timeslot']

            # Cancel the appointment
            if cancel_appointment(user, appointment_id, schedule_file, appointment_file):
                # Notify the MHW
                mhwp_email = get_email_by_username(selected_appointment['mhwp_username'])
                if mhwp_email:
                    subject = "Appointment Cancelled"
                    message = (
                        f"Dear {selected_appointment['mhwp_username']},\n\n"
                        f"The appointment with {user.username} on {date} during {timeslot} has been cancelled by the patient.\n\n"
                        "Regards,\nBreeze Mental Health Support System"
                    )
                    send_email_notification(mhwp_email, subject, message)
                else:
                    print("Error: Could not retrieve MHW's email address.")
            else:
                print("Failed to cancel the appointment.")
        except ValueError:
            print("Invalid input. Please enter a valid ID.")
    except FileNotFoundError:
        print(f"Error: {appointment_file} not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def cancel_appointment(user, appointment_id, schedule_file, appointment_file):
    """
    Allow a patient to cancel their appointment by appointment ID.
    Updates mhwp_schedule.csv to mark the slot as available (■).
    """
    try:
        # Load appointments.csv
        appointments = pd.read_csv(appointment_file)
        
        # Ensure the appointment ID exists and matches the user
        appointment_filter = (appointments['id'] == appointment_id) & \
                             (appointments['patient_username'] == user.username)

        if not appointment_filter.any():
            print(f"No matching appointment found for appointment ID: {appointment_id}.")
            return False

        # Retrieve appointment details
        appointment_row = appointments.loc[appointment_filter].iloc[0]
        mhwp_username = appointment_row['mhwp_username']
        date = appointment_row['date']
        timeslot = appointment_row['timeslot']

        # Cancel the appointment
        appointments.loc[appointment_filter, 'status'] = 'cancelled'
        appointments.to_csv(appointment_file, index=False)

        # Update mhwp_schedule.csv to mark the slot as available (■)
        try:
            schedule = pd.read_csv(schedule_file)
            time_slot_column = [col for col in schedule.columns if timeslot in col]
            if not time_slot_column:
                print(f"Time slot '{timeslot}' is invalid.")
                return False
            time_slot_column = time_slot_column[0]

            schedule_filter = (schedule['mhwp_username'] == mhwp_username) & (schedule['Date'] == date)
            schedule.loc[schedule_filter, time_slot_column] = "■"
            schedule.to_csv(schedule_file, index=False)
            print(f"Schedule updated: time slot '{timeslot}' is now available.")
        except FileNotFoundError:
            print("Error: mhwp_schedule.csv not found.")
        except Exception as e:
            print(f"Error updating schedule: {e}")
            return False

        print("Appointment cancelled successfully!")
        return True

    except FileNotFoundError:
        print("Error: appointments.csv not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    

def display_upcoming_appointments_with_mhwp(patient_username, appointments_file, assignments_file):
    """
    Display upcoming appointments for a patient with MHW names included.
    """
    try:
        # Load assignments to get MHW for the patient
        assignments = pd.read_csv(assignments_file, header=None, names=["patient_username", "mhwp_username"])
        mhwp_record = assignments[assignments['patient_username'] == patient_username]
        if mhwp_record.empty:
            print(f"No assigned MHW found for patient '{patient_username}'.")
            return
        mhwp_username = mhwp_record.iloc[0]['mhwp_username']

        # Load appointments for the patient
        appointments = pd.read_csv(appointments_file)
        user_appointments = appointments[appointments['patient_username'] == patient_username]

        if user_appointments.empty:
            print("\nNo appointments found for the next week.")
            return

        # Add MHW username column
        user_appointments['mhwp_username'] = mhwp_username

        # Convert dates to datetime and filter for the next week
        user_appointments['date'] = pd.to_datetime(user_appointments['date'], format="%Y/%m/%d")
        today = pd.to_datetime("today").normalize()
        next_week = today + pd.Timedelta(days=7)
        upcoming_appointments = user_appointments[
            (user_appointments['date'] >= today) & (user_appointments['date'] <= next_week)
        ]

        if upcoming_appointments.empty:
            print("\nNo appointments found for the next week.")
            return

        # Format and sort
        upcoming_appointments = upcoming_appointments.copy()  # Avoid SettingWithCopyWarning
        upcoming_appointments['date'] = upcoming_appointments['date'].dt.strftime("%Y/%m/%d")
        upcoming_appointments = upcoming_appointments.sort_values(by=['date', 'timeslot'])

        # Display the table
        print("\nYour appointments for the next week:")
        print(tabulate(
            upcoming_appointments[['date', 'mhwp_username', 'timeslot', 'status']],
            headers=['Date', 'MHWP', 'Time Slot', 'Status'],
            tablefmt="grid",
            showindex=False
        ))

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")





def handle_patient_menu(user):
    remind_to_complete_questionnaire(user.username)

    while True:
        print("\nPatient Options:")
        print("1. Account Management")
        print("2. Health & Wellbeing")
        print("3. Appointments & Records")
        print("4. Logout")

        main_choice = input("Select an option (1-4): ").strip()

        if main_choice == '1':  # Account Management
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

                        import pandas as pd
                        from config import USER_DATA_PATH

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
                        break
                elif account_choice == '6':
                    break  
                else:
                    print("Invalid choice, please try again.")
                    
                


        elif main_choice == '2':  # Health & Wellbeing
            while True:
                print("\nHealth & Wellbeing:")
                print("1. View Medical Records")
                print("2. Submit a Mood Questionnaire")
                print("3. Track Mood")
                print("4. Enter a Journaling")
                print("5. Explore Meditation Resources")
                print("6. Back to Main Menu")

                wellbeing_choice = input("Select an option (1-6): ").strip()

                if wellbeing_choice == '1':
                    print("Medical records feature coming soon...")
                elif wellbeing_choice == '2':
                    submit_questionnaire(user.username)      
                elif wellbeing_choice == '3':
                    handle_mood_tracking(user)
                elif wellbeing_choice == '4':
                    enter_journaling(user.username)  
                elif wellbeing_choice == '5':
                    handle_search_meditation()  
                elif wellbeing_choice == '6':
                    break  
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == '3':  # Appointments & Records
            while True:
                print("\nAppointments & Records:")
                print("1. Book/Cancel Appointment")
                print("2. Check Appointments")
                print("3. Leave a Comment for Your MHWP")
                print("4. Back to Main Menu")

                records_choice = input("Select an option (1-4): ").strip()

                if records_choice == '1':
                    import pandas as pd
            
                    while True:
                        print("\nBook/Cancel Appointment:")
                        print("1. Book an appointment")
                        print("2. Cancel an appointment")
                        print("3. Return to main menu")

                        appointment_choice = input("Select an option (1/2/3): ").strip()

                        if appointment_choice == "1":  # Book an appointment
                
                            book_appointment_with_schedule(user, "data/mhwp_schedule.csv", "data/assignments.csv", "data/appointments.csv")


                        elif appointment_choice == "2":  # Cancel an appointment
                            cancel_appointment_with_display(user, "data/mhwp_schedule.csv", "data/appointments.csv")
                
                        elif appointment_choice == "3":  # Return to main menu
                            print("Returning to main menu...")
                            break
                        
                elif records_choice == '2':
                    while True:
                        display_upcoming_appointments_with_mhwp(
                            user.username, 
                            "data/appointments.csv", 
                            "data/assignments.csv"
                        )
                
                        # Prompt user to return to main menu
                        print("\nPress '1' to return to the main menu.")
                        return_choice = input("Enter your choice: ").strip()
                
                        if return_choice == '1':
                            break  # Return to main menu
                        else:
                            print("Invalid choice. Please press '1' to return to the main menu.")


                elif records_choice == '3':
                    comment(user.username)


                elif records_choice == '4':
                    break  # Return to main menu
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == '4':  # Logout
            print("Logging out.")
            break

        else:
            print("Invalid choice, please try again.")



def handle_mood_tracking(user):
    print("\nMood Tracking")
    print("How are you feeling today?")
    print("1. Green - Very Good (Feeling great, energetic, positive)")
    print("2. Blue - Good (Calm, content, peaceful)")
    print("3. Yellow - Neutral (OK, balanced)")
    print("4. Orange - Not Great (Worried, uneasy)")
    print("5. Red - Poor (Distressed, anxious, depressed)")
    
    color_choice = input("Select your mood (1-5): ").strip()
    if color_choice in ["1", "2", "3", "4", "5"]:
        comments = input("Would you like to add any comments about your mood? ").strip()
        mood_entry = MoodEntry(user.username, color_choice, comments)
        mood_entry.save_mood_entry()
        
        display_mood_history(user.username)
    else:
        print("Invalid mood selection.")

def display_mood_history(username):
    print("\nYour recent mood history:")
    history = MoodEntry.get_user_mood_history(username)
    if not history.empty:
        print(history[['timestamp', 'color_code', 'comments']].head())
