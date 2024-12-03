import os
import csv
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
import calendar
from config import USER_DATA_PATH
from services.comment import view_comments
from services.patient_records import view_patient_records
from utils.notification import send_email_notification, get_email_by_username
from services.record import view_records_of_patient
from services.dashboard import display_dashboard


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
            print("No. | Patient      | Date       | Start - End    | Status")
            print("------------------------------------------------------------------")
            for idx, row in enumerate(appointments, start=1):
                print(
                    f"{idx:2d} | {row['patient_username']:<10} | {row['date']} | {row['timeslot']} | {row['status']}")

    except Exception as e:
        print(f"Error reading appointments: {str(e)}")

    return appointments


def generate_day_from_date(date_str):
    """
    Generate the day of the week based on the date.
    :param date_str: date string in the format of YYYY/MM/DD
    :return: The corresponding day of the week (e.g. "Monday")
    """
    try:
        return datetime.strptime(date_str, "%Y/%m/%d").strftime("%A")
    except ValueError:
        return "Invalid Date"



def generate_schedule_for_month(username, weekdays):
    """
    Generate a 1-month schedule based on user availability, including day names.
    :param username: Username of the MHW
    :param weekdays: List of weekday indices (e.g., [0, 3] for Monday and Thursday)
    :return: A list of schedules containing dates and their corresponding day names
    """
    today = datetime.today()
    end_date = today + timedelta(days=30)  # 1 month later

    schedule = []
    current_date = today
    while current_date <= end_date:
        if current_date.weekday() in weekdays:
            # Include both date and corresponding weekday name
            schedule.append((current_date.strftime("%Y/%m/%d"), calendar.day_name[current_date.weekday()]))
        current_date += timedelta(days=1)

    return schedule

def generate_time_slots(start_hour=9, end_hour=16):
    """
    Generate time slots in the format '09:00-10:00 (0)', '10:00-11:00 (1)', etc.
    :param start_hour: Start of the time slots (default: 9)
    :param end_hour: End of the time slots (default: 16)
    :return: A list of formatted time slots
    """
    time_slots = []
    for i, hour in enumerate(range(start_hour, end_hour)):
        start_time = f"{hour:02d}:00"
        end_time = f"{hour + 1:02d}:00"
        time_slots.append(f"{start_time}-{end_time} ({i})")
    return time_slots


def display_current_schedule(username, file_path):
    """
    Display the current open schedule for the MHW for the next month with pagination.
    """
    if not os.path.exists(file_path):
        print(f"Error: Schedule file '{file_path}' not found.")
        return

    try:
        # Read schedule data
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get headers
            user_data = [row for row in reader if row[0] == username]

        if not user_data:
            print("\nNo available schedule found for your account. Please set up your availability.")
            return

        # Pagination logic
        page_size = 10
        current_page = 0
        total_pages = (len(user_data) + page_size - 1) // page_size  # Calculate total pages

        while True:
            start_index = current_page * page_size
            end_index = start_index + page_size
            page_data = user_data[start_index:end_index]

            print(f"\nSchedule for the next month for {username} (Page {current_page + 1} of {total_pages}):")
            print(tabulate(page_data, headers=headers, tablefmt="grid"))
           
            # Legend for symbols
            print("\nLegend:")
            print("■ - Available")
            print("□ - Unavailable")
            print("▲ - Booked")
            print("● - Confirmed Appointment")
            
            # Pagination controls
            print("\nOptions:")
            print("1. Next page")
            print("2. Previous page")
            print("3. Return to main menu")

            choice = input("Select an option (1/2/3): ").strip()
            if choice == "1":
                if current_page < total_pages - 1:
                    current_page += 1
                else:
                    print("This is the last page.")
            elif choice == "2":
                if current_page > 0:
                    current_page -= 1
                else:
                    print("This is the first page.")
            elif choice == "3":
                print("Returning to main menu...")
                break
            else:
                print("Invalid choice. Please select a valid option.")

    except Exception as e:
        print(f"Error displaying schedule: {str(e)}")


def display_upcoming_appointments(username, file_path):
    """
    Display the confirmed and pending appointments for the next week for the MHW, sorted by date and time.
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

        # Filter for the next 7 days and the current MHW
        upcoming_appointments = appointments_df[
            (appointments_df['mhwp_username'] == username) &
            (appointments_df['date'] >= today) &
            (appointments_df['date'] <= today + pd.Timedelta(days=7)) &
            (appointments_df['status'].isin(['confirmed', 'pending']))
        ].copy()  # Use `.copy()` to avoid SettingWithCopyWarning

        if upcoming_appointments.empty:
            print("\nNo confirmed or pending appointments found for the next week.")
            return

        # Format the date column to remove time and ensure proper display as string
        upcoming_appointments['date'] = upcoming_appointments['date'].dt.strftime("%Y/%m/%d").astype(str)

        # Drop the mhwp_username column
        upcoming_appointments = upcoming_appointments.drop(columns=['mhwp_username'])

        # Sort appointments by date and timeslot
        upcoming_appointments = upcoming_appointments.sort_values(by=['date', 'timeslot'])

        # Display the upcoming appointments without the index column
        print(f"\nConfirmed and Pending Appointments for the next week for {username}:")
        print(tabulate(upcoming_appointments, headers="keys", tablefmt="grid", showindex=False))

    except Exception as e:
        print(f"Error displaying appointments: {str(e)}")





def modify_mhwp_schedule(user, option, dates=None, time_slot_indices=None):
    output_file = "data/mhwp_schedule.csv"
    if not os.path.exists(output_file):
        print(f"Error: Schedule file '{output_file}' not found.")
        return

    try:
        with open(output_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Read headers
            all_schedules = list(reader)

        # Add "Day" to headers if missing
        if "Day" not in headers:
            headers.insert(2, "Day")  # Insert after "Date"

        # Ensure all rows have a "Day" value
        for row in all_schedules:
            if len(row) < len(headers):
                date_str = row[1]  # Get "Date" column
                day_name = generate_day_from_date(date_str)
                row.insert(2, day_name)

        # Update user's schedule
        user_schedule = [row for row in all_schedules if row[0] == user.username]
        other_users = [row for row in all_schedules if row[0] != user.username]

        if option == 1:  # Take a Leave
            updated_user_schedule = [row for row in user_schedule if row[1] not in dates]

        elif option == 2:  # Change Time Slots
            updated_user_schedule = user_schedule[:]
            for date in dates:
                matching_row = next((row for row in updated_user_schedule if row[1] == date), None)
                if not matching_row:
                    print(f"No schedule found for the date: {date}")
                    continue

                # Update time slots
                for idx in range(len(headers[3:])):  # Slots start from 3rd column
                    matching_row[idx + 3] = "■" if idx in time_slot_indices else "□"

        # Combine updated user schedule with other users
        updated_schedules = other_users + updated_user_schedule

        with open(output_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers
            writer.writerows(updated_schedules)  # Write all data

    except Exception as e:
        print(f"Error modifying schedule: {str(e)}")


def setup_mhwp_schedule(user):
    """Set up availability schedule for the Mental Health Worker with slots."""
    print("\nSetup Your Availability")
    output_file = "data/mhwp_schedule.csv"
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                try:
                    headers = next(reader)
                except StopIteration:
                    print("\nError: The schedule file is empty or has no headers.")
                    return
                expected_columns = [
                    "mhwp_username", "Date", "Day",
                    "09:00-10:00 (0)", "10:00-11:00 (1)", "11:00-12:00 (2)",
                    "12:00-13:00 (3)", "13:00-14:00 (4)", "14:00-15:00 (5)", "15:00-16:00 (6)"
                ]
                if headers != expected_columns:
                    print("\nError: The schedule file has incorrect headers.")
                    return

                for row in reader:
                    if not row:
                        continue
                    if row[0] == user.username:
                        print("\nYou have already set up your availability.")
                        print("Returning to the Mental Health Worker Options menu...\n")
                        return

        except FileNotFoundError:
            print(f"\nError: File '{output_file}' not found.")
            return
        except Exception as e:
            print(f"\nError reading the file: {e}")
            return

    print("\nDay Index Reference:")
    print("Monday (0), Tuesday (1), Wednesday (2), Thursday (3), Friday (4), Saturday (5), Sunday (6)")

    weekday_indices = input("Enter the indices of your available weekdays, separated by commas (e.g., 0,3): ").strip()
    weekday_indices = [int(idx) for idx in weekday_indices.split(",") if idx.isdigit()]

    available_dates = generate_schedule_for_month(user.username, weekday_indices)

    start_hour, end_hour = 9, 16
    time_slots = generate_time_slots(start_hour, end_hour)

    headers = ["mhwp_username", "Date", "Day"] + time_slots
    rows = []
    for date, _ in available_dates:
        day_name = generate_day_from_date(date)  # Calculate day from date
        rows.append([user.username, date, day_name] + ["□" for _ in time_slots])

    print("\nGenerated Schedule for the Next 1 Month:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    selected_indices = input("\nEnter the indices of your available time slots, separated by commas (e.g., 0,2,4): ").strip()
    selected_indices = [int(idx) for idx in selected_indices.split(",") if idx.isdigit()]

    for row in rows:
        for idx in selected_indices:
            row[idx + 3] = "■"  # Update slots (offset by 3 for username, date, and day)

    print("\nYour updated schedule (applying changes to all selected weekdays):")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    updated_data = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                try:
                    current_headers = next(reader)
                except StopIteration:
                    print("\nError: The schedule file is empty. Writing new data...")
                    current_headers = headers

                if current_headers != headers:
                    print("\nError: The file has incorrect headers.")
                    return

                updated_data = [
                    row for row in reader if row and row[0] != user.username
                ]
        except Exception as e:
            print(f"\nError reading the file: {e}")
            return

    updated_data.extend(rows)
    try:
        with open(output_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(updated_data)
        print(f"\nYour schedule has been successfully saved to {output_file}.")
    except Exception as e:
        print(f"\nError writing to the file: {e}")

def manage_appointment_action(user, manage_choice, appointments_file, schedule_file):
    """
    Handles confirming or canceling appointments for the MHW.
    """
    appointments = list_appointments_for_mhw(user.username, appointments_file)
    if not appointments:
        return  # Return to appointment management menu

    appointment_id = input("Enter the No. of the appointment to manage: ").strip()
    try:
        appointment_id = int(appointment_id) - 1
        if 0 <= appointment_id < len(appointments):
            selected_appointment = appointments[appointment_id]
            action = "confirm" if manage_choice == "2" else "cancel"

            # Enforce status constraints
            if action == "confirm" and selected_appointment['status'] != "pending":
                print("Only pending appointments can be confirmed. Please try again.")
                return
            elif action == "cancel" and selected_appointment['status'] not in ["pending", "confirmed"]:
                print("Only pending or confirmed appointments can be cancelled. Please try again.")
                return

            # Update appointment status
            update_appointment_status(selected_appointment, action, appointments_file)

            # Update MHW schedule
            update_schedule(selected_appointment, action, schedule_file)

            # Notify the patient
            notify_patient(user.username, selected_appointment, action)
        else:
            print("Invalid ID. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid appointment ID.")


### Helper Functions

def update_appointment_status(selected_appointment, action, appointments_file):
    """
    Updates the status of the selected appointment in appointments.csv.
    """
    try:
        appointments_df = pd.read_csv(appointments_file)
        appointment_filter = (
            (appointments_df['patient_username'] == selected_appointment['patient_username']) &
            (appointments_df['mhwp_username'] == selected_appointment['mhwp_username']) &
            (appointments_df['date'] == selected_appointment['date']) &
            (appointments_df['timeslot'] == selected_appointment['timeslot'])
        )
        if appointment_filter.any():
            new_status = "confirmed" if action == "confirm" else "cancelled"
            appointments_df.loc[appointment_filter, 'status'] = new_status
            appointments_df.to_csv(appointments_file, index=False)
            print(f"Appointment successfully {action}ed!")
        else:
            print("Appointment not found.")
    except FileNotFoundError:
        print("Error: appointments.csv file not found.")
    except Exception as e:
        print(f"Error processing appointment: {e}")


def update_schedule(selected_appointment, action, schedule_file):
    """
    Updates the schedule for the selected appointment in mhwp_schedule.csv.
    """
    try:
        schedule_df = pd.read_csv(schedule_file)
        time_slot_column = [col for col in schedule_df.columns if selected_appointment['timeslot'] in col]
        if not time_slot_column:
            print(f"Time slot '{selected_appointment['timeslot']}' is invalid.")
            return
        time_slot_column = time_slot_column[0]
        schedule_filter = (
            (schedule_df['mhwp_username'] == selected_appointment['mhwp_username']) &
            (schedule_df['Date'] == selected_appointment['date'])
        )
        # Update schedule based on action
        if action == "confirm":
            schedule_df.loc[schedule_filter, time_slot_column] = "●"  # Mark as confirmed
        elif action == "cancel":
            schedule_df.loc[schedule_filter, time_slot_column] = "■"  # Mark as available
        schedule_df.to_csv(schedule_file, index=False)
        print(f"Schedule updated: time slot '{selected_appointment['timeslot']}' updated for {action}.")
    except FileNotFoundError:
        print("Error: mhwp_schedule.csv not found.")
    except Exception as e:
        print(f"Error updating schedule: {e}")


def notify_patient(mhwp_username, selected_appointment, action):
    """
    Sends an email notification to the patient regarding the appointment action.
    """
    patient_email = get_email_by_username(selected_appointment['patient_username'])
    if patient_email:
        subject = f"Your appointment has been {action}ed"
        if action == "confirm":
            message = (
                f"Dear {selected_appointment['patient_username']},\n\n"
                f"Your appointment with {mhwp_username} on {selected_appointment['date']} "
                f"at {selected_appointment['timeslot']} has been confirmed.\n\n"
                "Regards,\nBreeze Mental Health Support System"
            )
        elif action == "cancel":
            message = (
                f"Dear {selected_appointment['patient_username']},\n\n"
                f"Your appointment with {mhwp_username} on {selected_appointment['date']} "
                f"at {selected_appointment['timeslot']} has been cancelled.\n\n"
                "Regards,\nBreeze Mental Health Support System"
            )
        send_email_notification(patient_email, subject, message)
    else:
        print("Error: Could not retrieve patient's email address.")


def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. Change Email")
        print("4. Change Emergency Email")
        print("5. View Patient Records")
        print("6. Manage Appointments")
        print("7. Set Up Your Availability")
        print("8. View Your Current Schedule")
        print("9. Modify Your Availability")
        print("10.Delete Account")
        print("11. Logout")

        mhwp_choice = input("Select an option (1-11): ").strip()

        if mhwp_choice == '1':  # Update username
            try:
                new_username = input("Enter new username: ").strip()
                if not new_username:
                    print("Username cannot be empty.")
                    continue

                user_df = pd.read_csv(USER_DATA_PATH)
                if new_username in user_df['username'].values:
                    print("Username already exists. Please choose a different one.")
                    continue

               
                if user.update_info(new_username=new_username):
                    continue
                else:
                    print("Failed to update username. Please try again.")
            except Exception as e:
                print(f"Error updating username: {str(e)}")
        
        elif mhwp_choice == '2':  # Change password
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)

            if user.update_info(new_password=new_password):
                print("Password updated successfully!")
            else:
                print("Failed to update password. Try again.")

        elif mhwp_choice == '3':  # Change email
            new_email = input("Enter new email: ").strip()
            if not new_email:  
                print("Email cannot be empty. Please try again.")
                continue

            if user.update_info(new_email=new_email):
                print("Email updated successfully!")
            else:
                print("Failed to update email. Try again.")
                
        elif mhwp_choice == '4':  # Change emergency email
            new_emergency_email = input("Enter new emergency email: ").strip()
            if not new_emergency_email:  
                print("Emergency email cannot be empty. Please try again.")
                continue

            if user.update_info(new_emergency_email=new_emergency_email):
                print("Emergency email updated successfully!")
            else:
                print("Failed to update emergency email. Try again.")

        elif mhwp_choice == '5':  # View Patient Records
            try:
                print("\nViewing patient records...")
                view_patient_records(user.username)  
            except Exception as e:
                print(f"Error viewing patient records: {str(e)}")

        elif mhwp_choice == '6':  # Manage Appointments
            import pandas as pd
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
                    manage_appointment_action(user, manage_choice, "data/appointments.csv", "data/mhwp_schedule.csv")

                elif manage_choice == "4":  # Back to MMHW Options
                    print("Returning to main menu...")
                    break


        elif mhwp_choice == '7':  # Set up availability
            setup_mhwp_schedule(user)

        elif mhwp_choice == '8':  # Schedule and Appointment Management
            
            while True:
                print("\nSchedule and Appointment Management:")
                print("1. View schedule for the next month")
                print("2. View appointments for the next week")
                print("3. Back to main menu")

                schedule_choice = input("Select an option (1-3): ").strip()

                if schedule_choice == "1":  # View schedule for the next month
                    display_current_schedule(user.username, "data/mhwp_schedule.csv")
                elif schedule_choice == "2":  # View detailed appointments for the next week
                    display_upcoming_appointments(user.username, "data/appointments.csv")
                elif schedule_choice == "3":  # Back to main menu
                    print("Returning to main menu...")
                    break
                else:
                    print("Invalid choice. Please select a valid option.")


        elif mhwp_choice == '9':  # Modify Your Availability
            while True:
                print("\nModify Your Availability Options:")
                print("1. Take a Leave (Adjust availability for specific dates)")
                print("2. Change Time Slots for Specific Dates")
                print("3. Back to main menu")

                modify_choice = input("Select an option (1-3): ").strip()

                if modify_choice == '1':  # Take a Leave
                    import pandas as pd
                    leave_dates = input("\nEnter the dates you want to take leave for (YYYY/MM/DD), separated by commas: ").strip()
                    leave_dates = [date.strip() for date in leave_dates.split(",")]

                    # File path for schedule data
                    file_path = "data/mhwp_schedule.csv"

                    try:
                        schedule_df = pd.read_csv(file_path)

                        # Filter schedules for the current user
                        user_schedule = schedule_df[schedule_df['mhwp_username'] == user.username]

                        if user_schedule.empty:
                            print(f"No schedule found for user '{user.username}'.")
                            continue

                        # Check for booked or confirmed time slots on leave dates
                        conflicts = []
                        for date in leave_dates:
                            if date in user_schedule['Date'].values:
                                day_schedule = user_schedule[user_schedule['Date'] == date]
                                for col in day_schedule.columns[3:]:  # Time slot columns
                                    if day_schedule.iloc[0][col] in ["●", "▲"]:  # Check for booked or confirmed
                                        conflicts.append(date)
                                        break

                        if conflicts:
                            print("\nYou have booked or confirmed time slots on the following dates:")
                            for conflict in conflicts:
                                print(f" - {conflict}")
                            print("Please cancel all bookings on these dates before taking leave.")
                            continue

                        # Modify availability for the selected dates
                        for date in leave_dates:
                            if date in user_schedule['Date'].values:
                                schedule_df.loc[
                                    (schedule_df['mhwp_username'] == user.username) & (schedule_df['Date'] == date),
                                    schedule_df.columns[3:]  # Adjust all time slots
                                ] = "□"  # Mark all time slots as unavailable

                        # Save the updated schedule
                        schedule_df.to_csv(file_path, index=False)
                        print("\nYour availability has been updated. All available slots for the selected dates are now unavailable.")

                    except FileNotFoundError:
                        print(f"Error: File '{file_path}' not found.")
                    except Exception as e:
                        print(f"Error processing leave request: {str(e)}")





                elif modify_choice == '2':  # Change Time Slots

                    file_path = "data/mhwp_schedule.csv"

                    try:

                        with open(file_path, "r", encoding="utf-8") as file:

                            reader = csv.reader(file)

                            headers = next(reader)  # Read headers

                            all_schedules = list(reader)

                        # Generate time slots and ensure headers match time slots

                        time_slots = ["09:00-10:00 (0)", "10:00-11:00 (1)", "11:00-12:00 (2)",

                                      "12:00-13:00 (3)", "13:00-14:00 (4)", "14:00-15:00 (5)", "15:00-16:00 (6)"]

                        expected_headers = ["mhwp_username", "Date", "Day"] + time_slots

                        # Expand headers if necessary

                        if len(headers) < len(expected_headers):
                            headers = expected_headers

                        # Extract current user's schedule

                        current_user_schedule = [row for row in all_schedules if row[0] == user.username]

                        # Display current schedule

                        print("\nCurrent Schedule:")

                        print(tabulate(current_user_schedule, headers=headers, tablefmt="grid"))

                        # Prompt user to enter dates

                        modify_dates = input(
                            "\nEnter the dates you want to modify (YYYY/MM/DD), separated by commas: ").strip()

                        if not modify_dates:  # Check if user enters nothing

                            print("\nNo dates entered. Returning to menu...")

                            continue

                        modify_dates = [date.strip() for date in modify_dates.split(",")]

                        updated_user_schedule = current_user_schedule

                        num_slots = len(time_slots)

                        for date in modify_dates:

                            matching_row = next((row for row in updated_user_schedule if row[1] == date), None)

                            if not matching_row:
                                print(f"\nNo schedule found for the date: {date}")

                                continue

                            # Extract the day name

                            day_name = matching_row[2] if len(matching_row) > 2 else "Unknown"

                            # Ensure row has enough columns for all time slots

                            while len(matching_row) < len(expected_headers):
                                matching_row.append("□")

                            # Display current time slots in horizontal table

                            row_data = matching_row[3:]  # Start from time slots

                            print(f"\nCurrent Time Slots for {date} ({day_name}):")

                            print(tabulate([["Date"] + time_slots, [date] + row_data], headers="firstrow",
                                           tablefmt="grid"))

                            # Select the current available slot to move

                            while True:

                                try:

                                    current_index = int(input(
                                        f"\nEnter the index of the currently available slot you want to move (e.g., 0-6): ").strip())

                                    if 0 <= current_index < num_slots:

                                        if row_data[current_index] == "■":

                                            break  # Valid selection, exit loop

                                        elif row_data[current_index] in ["▲", "●"]:

                                            print(
                                                f"\nThe current slot {time_slots[current_index]} cannot be modified due to the appointment.")

                                        else:

                                            print("Invalid selection. Please choose a valid available slot (■).")

                                    else:

                                        print("Invalid index. Please enter a valid slot index.")

                                except ValueError:

                                    print("Invalid input. Please enter a valid index as an integer.")

                            # Select the target slot to change to

                            while True:

                                try:

                                    target_index = int(input(
                                        f"\nEnter the index of the target slot to make available (e.g., 0-6): ").strip())

                                    if 0 <= target_index < num_slots:

                                        if row_data[target_index] == "□":

                                            break  # Valid target slot, exit loop

                                        elif row_data[target_index] in ["▲", "●"]:

                                            print(
                                                f"\nThe target slot {time_slots[target_index]} cannot be modified due to the appointment.")

                                        else:

                                            print("Invalid selection. Please choose an unavailable slot (□).")

                                    else:

                                        print("Invalid index. Please enter a valid slot index.")

                                except ValueError:

                                    print("Invalid input. Please enter a valid index as an integer.")

                            # Perform the swap

                            row_data[current_index], row_data[target_index] = "□", "■"

                            matching_row[3:] = row_data

                        # Combine updated user schedule with other users

                        other_users = [row for row in all_schedules if row[0] != user.username]

                        updated_schedules = other_users + updated_user_schedule

                        # Save the updated schedule back to the file

                        with open(file_path, "w", newline='', encoding="utf-8") as file:

                            writer = csv.writer(file)

                            writer.writerow(headers)  # Write headers

                            writer.writerows(updated_schedules)  # Write updated data

                        print("\nYour updated time slots have been saved successfully!")

                        # Display the updated schedule

                        print("\nUpdated Schedule (After Modifications):")

                        updated_user_schedule_display = [row for row in updated_schedules if row[0] == user.username]

                        print(tabulate(updated_user_schedule_display, headers=headers, tablefmt="grid"))


                    except Exception as e:

                        print(f"Error modifying time slots: {str(e)}")


                elif modify_choice == '3':  # Back to main menu
                    break
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")

        elif mhwp_choice == '10':
            confirm = input("Confirm delete account? (yes/no): ").strip()
            if confirm.lower() == "yes":
                user.delete_from_csv()
                print("Account deleted successfully.")
                return
        elif mhwp_choice == '11':  # Logout
            break

        else:
            print("Invalid choice. Please select an option between 1 and 11.")
