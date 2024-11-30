import os
from services.mood_tracking import MoodEntry
from services.meditation import handle_search_meditation
from services.comment import add_comment,get_mhwp_for_patient
from services.questionnaire import submit_questionnaire,remind_to_complete_questionnaire
from services.journaling import enter_journaling
from utils.notification import send_email_notification, get_email_by_username
import pandas as pd
from tabulate import tabulate  
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
            appointments = pd.DataFrame(columns=['patient_username', 'mhwp_username', 'date', 'timeslot', 'status'])

        # Check for overlapping appointments
        overlapping_appointment = appointments[
            (appointments['mhwp_username'] == mhwp_username) &
            (appointments['date'] == date) &
            (appointments['timeslot'] == timeslot)
        ]
        if not overlapping_appointment.empty:
            print(f"The selected time slot '{timeslot}' overlaps with an existing appointment. Please choose another.")
            return False
        
        # Record the new appointment in appointments.csv
        new_appointment = {
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

        #print("Appointment booked successfully!")
        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def cancel_appointment(user, date, timeslot, schedule_file, appointment_file):
    """
    Allow a patient to cancel their appointment.
    Updates mhwp_schedule.csv to mark the slot as available (■).
    """
    if user.role != "patient":
        print("Only patients can cancel appointments.")
        return False

    if not user.username:
        print("Error: username is not set. Please log in or register.")
        return False

    try:
        # Load appointments.csv
        appointments = pd.read_csv(appointment_file)
        appointment_filter = (appointments['patient_username'] == user.username) & \
                             (appointments['date'] == date) & \
                             (appointments['timeslot'] == timeslot)

        if not appointment_filter.any():
            print("No matching appointment found.")
            return False

        # Retrieve MHW username from the appointment
        mhwp_username = appointments.loc[appointment_filter, 'mhwp_username'].values[0]

        # Cancel the appointment
        appointments.loc[appointment_filter, 'status'] = 'cancelled'
        appointments.to_csv(appointment_file, index=False)
        #print("Appointment cancelled successfully!")

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

        return True

    except FileNotFoundError:
        print("Error: appointments.csv not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
def display_upcoming_appointments_for_patient(username, file_path):
        """
        Display the appointments for the next week for a patient.
        """
        if not os.path.exists(file_path):
                print(f"Error: Appointment file '{file_path}' not found.")
                return

        try:
                # Read appointments file
                appointments_df = pd.read_csv(file_path)

                # Ensure date format matches the file
                appointments_df['date'] = pd.to_datetime(appointments_df['date'], format="%Y/%m/%d")

                # Get today's date
                today = pd.to_datetime("today").normalize()

                # Filter for the next 7 days for the patient
                upcoming_appointments = appointments_df[
                        (appointments_df['patient_username'] == username) &
                        (appointments_df['date'] >= today) &
                        (appointments_df['date'] <= today + pd.Timedelta(days=7))
                ]

                if upcoming_appointments.empty:
                        print("\nNo appointments found for the next week.")
                        return

                # Create a copy to avoid SettingWithCopyWarning
                upcoming_appointments = upcoming_appointments.copy()

                # Format the date column to remove time and ensure proper display
                upcoming_appointments.loc[:, 'date'] = upcoming_appointments['date'].dt.strftime("%Y/%m/%d")

                # Sort appointments by date and timeslot
                upcoming_appointments = upcoming_appointments.sort_values(by=['date', 'timeslot'])

                # Display the upcoming appointments without the index column
                print(f"\nYour appointments for the next week:")
                print(tabulate(upcoming_appointments, headers="keys", tablefmt="grid", showindex=False))

        except Exception as e:
                print(f"Error displaying appointments: {str(e)}")
def handle_patient_menu(user):
    
    remind_to_complete_questionnaire(user.username)
    
    while True:
        print("\nPatient Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. Change email")
        print("4. Change emergency email")
        print("5. View Medical Records")
        print("6. Book/Cancel Appointment")
        print("7. Check Appointments")
        print("8. Enter a Journaling")
        print("9. Submit a Mood Questionnaire")
        print("10. Leave a Comment for Your MHWP")
        print("11. Explore Meditation Resources")
        print("12. Delete Account")
        print("13. Track Mood")
        print("14. Logout")
        
        patient_choice = input("Select an option (1-14): ")
        
        if patient_choice == '1':
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
                    print(f"Username successfully updated to {new_username}")
                else:
                    print("Failed to update username. Please try again.")
            except Exception as e:
                print(f"Error updating username: {str(e)}")

            new_username = input("Enter new username: ").strip()
            user.update_info(new_username=new_username)
            
        elif patient_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)
            
        elif patient_choice == '3':  # new funcs to change email
            new_email = input("Enter new email: ").strip()
            if user.update_info(new_email=new_email):  
                print("Email updated successfully!")
            else:
                print("Failed to update email. Try again.")
                
        elif patient_choice == '4':  # new option for emergency email
            new_emergency_email = input("Enter new emergency email: ").strip()
            if user.update_info(new_emergency_email=new_emergency_email):
                print("Emergency email updated successfully!")
            else:
                print("Failed to update emergency email. Try again.")
                
        elif patient_choice == '5':
            print("Medical records feature coming soon...")

        elif patient_choice == '6':  # Book/Cancel appointment
            import pandas as pd
            from utils.notification import send_email_notification, get_email_by_username
            while True:
                print("\nBook/Cancel Appointment:")
                print("1. Book an appointment")
                print("2. Cancel an appointment")
                print("3. Return to main menu")

                appointment_choice = input("Select an option (1/2/3): ").strip()

                if appointment_choice == "1":  # Book an appointment
                    date = input("Enter appointment date (YYYY/MM/DD): ").strip()

                    # Retrieve the assigned MHW for the patient
                    try:
                        assignments = pd.read_csv("data/assignments.csv", header=None, names=["patient_username", "mhwp_username"])
                        mhwp_record = assignments[assignments['patient_username'] == user.username]
                        if mhwp_record.empty:
                            print(f"No assigned MHW found for patient '{user.username}'.")
                            continue
                        mhwp_username = mhwp_record.iloc[0]['mhwp_username']
                    except FileNotFoundError:
                        print("Error: assignments.csv file not found.")
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        continue

                    # Display the MHW's schedule
                    try:
                        schedule = pd.read_csv("data/mhwp_schedule.csv")
                        mhwp_schedule = schedule[(schedule['mhwp_username'] == mhwp_username) & (schedule['Date'] == date)]

                        if mhwp_schedule.empty:
                            print(f"No schedule found for MHW '{mhwp_username}' on {date}.")
                            continue

                        print(f"\nSchedule for MHW '{mhwp_username}' on {date}:")
                        print("Slot Number | Time Slot      | Availability")
                        time_slots = [
                            "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
                            "13:00-14:00", "14:00-15:00", "15:00-16:00"
                        ]
                        for idx, slot in enumerate(time_slots):
                            column_name = f"{slot} ({idx})"
                            if column_name in mhwp_schedule.columns:
                                availability = mhwp_schedule.iloc[0][column_name]
                                print(f"{idx:<11} | {slot:<13} | {availability}")

                        # Choose a time slot number
                        slot_index = input("\nEnter the slot number to book (0-6): ").strip()
                        try:
                            slot_index = int(slot_index)
                            if slot_index < 0 or slot_index >= len(time_slots):
                                print("Invalid slot number. Please try again.")
                                continue

                            # Retrieve the corresponding time slot
                            timeslot = time_slots[slot_index]

                            # Attempt to book the appointment
                            if book_appointment(user, date, timeslot, "data/mhwp_schedule.csv", "data/assignments.csv", "data/appointments.csv"):
                                print("Appointment booked successfully!")

                                # Send an email notification to the MHW
                                mhwp_email = get_email_by_username(mhwp_username)
                                if mhwp_email:
                                    subject = "New Appointment Booked"
                                    message = (
                                        f"Dear {mhwp_username},\n\n"
                                        f"An appointment has been booked by {user.username} on {date} during {timeslot}.\n\n"
                                        "Regards,\nMental Health Support System"
                                    )
                                    send_email_notification(mhwp_email, subject, message)
                                    # print(f"Notification email sent to MHW: {mhwp_username}.")
                                else:
                                    print("Error: Could not retrieve MHW's email address.")
                            else:
                                print("Failed to book the appointment. Try again.")
                        except ValueError:
                            print("Invalid input. Please enter a valid slot number.")
                    except FileNotFoundError:
                        print("Error: mhwp_schedule.csv file not found.")
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        continue

                elif appointment_choice == "2":  # Cancel an appointment
                    try:
                        # Load and display the patient's appointments
                        appointments = pd.read_csv("data/appointments.csv")
                        user_appointments = appointments[appointments['patient_username'] == user.username]

                        if user_appointments.empty:
                            print("No appointments found to cancel.")
                            continue

                        # Display appointment list
                        print("\nYour current appointments:")
                        user_appointments = user_appointments.reset_index(drop=True)
                        user_appointments['ID'] = user_appointments.index + 1
                        print(user_appointments[['ID', 'date', 'timeslot', 'status']])

                        # Enter the ID to cancel the appointment
                        appointment_id = input("\nEnter the ID of the appointment to cancel: ").strip()
                        try:
                            appointment_id = int(appointment_id) - 1
                            if appointment_id < 0 or appointment_id >= len(user_appointments):
                                print("Invalid ID. Please try again.")
                                continue

                            # Retrieve the selected appointment record
                            selected_appointment = user_appointments.iloc[appointment_id]
                            date = selected_appointment['date']
                            timeslot = selected_appointment['timeslot']

                            # Cancel the appointment
                            if cancel_appointment(user, date, timeslot, "data/mhwp_schedule.csv", "data/appointments.csv"):
                                print("Appointment cancelled successfully!")

                                # Send an email notification to the MHW
                                mhwp_email = get_email_by_username(selected_appointment['mhwp_username'])
                                if mhwp_email:
                                    subject = "Appointment Cancelled"
                                    message = (
                                        f"Dear {selected_appointment['mhwp_username']},\n\n"
                                        f"The appointment with {user.username} on {date} during {timeslot} has been cancelled by the patient.\n\n"
                                        "Regards,\nMental Health Support System"
                                    )
                                    send_email_notification(mhwp_email, subject, message)
                                    # print(f"Notification email sent to MHW: {selected_appointment['mhwp_username']}.")
                                else:
                                    print("Error: Could not retrieve MHW's email address.")
                            else:
                                print("Failed to cancel the appointment.")
                        except ValueError:
                            print("Invalid input. Please enter a valid ID.")
                    except FileNotFoundError:
                        print("Error: appointments.csv not found.")
                    except Exception as e:
                        print(f"Unexpected error: {e}")

                elif appointment_choice == "3":  # Return to main menu
                    print("Returning to main menu...")
                    break

                else:
                    print("Invalid choice. Please select a valid option.")

        elif patient_choice == '7':  # View upcoming appointments
                while True:
                        display_upcoming_appointments_for_patient(user.username, "data/appointments.csv")
                        
                        
                        print("\nPress '1' to return to the main menu.")
                        return_choice = input("Enter your choice: ").strip()
                        
                        if return_choice == '1':
                                break 
                        else:
                                print("Invalid choice. Please press '1' to return to the main menu.")

        elif patient_choice == '8':  # Journaling
            enter_journaling(user.username)
                
        elif patient_choice == '9':  # Questionnaire
            submit_questionnaire(user.username)      
    
        elif patient_choice == '10':  # Comment
            mhwp_username = get_mhwp_for_patient(user.username)
            if mhwp_username:
                try:
                    rating = float(input("Enter a rating for your MHWP (0-5): ").strip())
                    comment = input("Enter your comment for your MHWP: ").strip()
                    add_comment(user.username, mhwp_username, rating, comment)
                except ValueError:
                    print("Invalid input. Rating must be a number.")
            else:
                print("Unable to find your MHWP. Comment not saved.")
                       
        elif patient_choice == '11':  # Meditation
            handle_search_meditation()  
            
        elif patient_choice == '12':
            confirm = input("Confirm delete account? (yes/no): ")
            if confirm.lower() == "yes":
                user.delete_from_csv()
                print("Account deleted successfully.")
                break
            
        elif patient_choice == '13':
            handle_mood_tracking(user)
            
        elif patient_choice == '14':
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
