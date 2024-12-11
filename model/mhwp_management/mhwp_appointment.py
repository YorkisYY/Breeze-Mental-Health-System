import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
from datetime import datetime, timedelta
from utils.notification import send_email_notification, get_email_by_username
from config import *


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

def generate_time_slots(start_hour=set_start_hour, end_hour=set_end_hour):
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

    # """
    # Generate time slots with index and 12-hour format
    #  '9-10am (0)', '10-11am (1)', etc.
    # :param start_hour: Start of the time slots (default: 9)
    # :param end_hour: End of the time slots (default: 16)
    # :return: A list of formatted time slots
    # """
    # return [f"{hour}-{hour+1}{'am' if hour < 12 else 'pm'} ({i})" 
    #         for i, hour in enumerate(range(start_hour, end_hour))]

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


def setup_mhwp_schedule(user,file_path=SCHEDULE_DATA_PATH): # choice 1, setup availability schedule(old style)
    """Set up availability schedule for the Mental Health Worker with slots."""
    print("\nSetup Your Availability")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
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
            print(f"\nError: File '{file_path}' not found.")
            return
        except Exception as e:
            print(f"\nError reading the file: {e}")
            return
    print("\nDay Index Reference:")
    print("Monday (0), Tuesday (1), Wednesday (2), Thursday (3), Friday (4), Saturday (5), Sunday (6)")
    while True:
        weekday_indices = input(
            "Enter the indices of your available weekdays, separated by commas (e.g., 0,3): ").strip()
        # Validate user input for correct format and range
        try:
            weekday_indices = [int(idx) for idx in weekday_indices.split(",") if idx.isdigit()]
            if all(0 <= idx <= 6 for idx in weekday_indices):
                break
            else:
                print("Error: Please enter valid indices between 0 and 6 only.")
        except ValueError:
            print("Error: Please enter valid indices between 0 and 6 only.")
    available_dates = generate_schedule_for_month(user.username, weekday_indices)
    time_slots = generate_time_slots(start_hour=set_start_hour, end_hour=set_end_hour)
    headers = ["mhwp_username", "Date", "Day"] + time_slots
    rows = []
    for date, _ in available_dates:
        day_name = generate_day_from_date(date)  # Calculate day from date
        rows.append([user.username, date, day_name] + ["□" for _ in time_slots])

    print("\nGenerated Schedule for the Next 1 Month:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    while True:
        selected_indices = input(
            "\nEnter the indices of your available time slots, separated by commas (e.g., 0,2,4): ").strip()
        try:
            selected_indices = [int(idx) for idx in selected_indices.split(",") if idx.isdigit()]
            if all(0 <= idx <= 6 for idx in selected_indices):  
                break
            else:
                print("Error: Please enter valid indices between 0 and 6 only.")
        except ValueError:
            print("Error: Please enter valid indices between 0 and 6 only.")

    for row in rows:
        for idx in selected_indices:
            row[idx + 3] = "■"  
    print("\nYour updated schedule (applying changes to all selected weekdays):")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    updated_data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
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
        with open(file_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(updated_data)
        print(f"\nYour schedule has been saved successfully.")
    except Exception as e:
        print(f"\nError writing to the file: {e}")

def update_appointment_status(selected_appointment, action, appointments_file=APPOINTMENTS_DATA_PATH):
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

def update_schedule(selected_appointment, action, schedule_file=SCHEDULE_DATA_PATH):
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

def notify_mhwp(mhwp_username, selected_appointment, action):
    """
    Sends an email notification to the patient regarding the appointment action.
    """
    mhwp_email = get_email_by_username(mhwp_username)
    if mhwp_email:
        subject = f"Your appointment has been successfully {action}ed"
        if action == "confirm":
            message = (
                f"Dear {mhwp_username},\n\n"
                f"Your appointment with {selected_appointment['patient_username']} on {selected_appointment['date']} "
                f"at {selected_appointment['timeslot']} has been successfully confirmed.\n\n"
                "Regards,\nBreeze Mental Health Support System"
            )
        elif action == "cancel":
            message = (
                f"Dear {mhwp_username},\n\n"
                f"Your appointment with {selected_appointment['patient_username']} on {selected_appointment['date']} "
                f"at {selected_appointment['timeslot']} has been successfully cancelled.\n\n"
                "Regards,\nBreeze Mental Health Support System"
            )
        send_email_notification(mhwp_email, subject, message)
    else:
        print("Error: Could not retrieve mhwp's email address.")

        
def manage_appointment_action(user, manage_choice, appointments_file=APPOINTMENTS_DATA_PATH, schedule_file=SCHEDULE_DATA_PATH):
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
            update_appointment_status(selected_appointment, action, appointments_file)
            update_schedule(selected_appointment, action, schedule_file)
            notify_patient(user.username, selected_appointment, action)
            notify_mhwp(user.username, selected_appointment, action)
        else:
            print("Invalid ID. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid appointment ID.")
        

def list_appointments_for_mhw(mhw_username, file_path=APPOINTMENTS_DATA_PATH):
    """List appointments for the currently logged-in MHW"""
    appointments = []
    if not exists(file_path):
        print(f"Error: Appointment record file '{file_path}' not found")
        return appointments

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            today = datetime.today().date()
            for row in reader:
                appointment_date=datetime.strptime(row['date'], "%Y/%m/%d").date()
                if (
                    row['mhwp_username'] == mhw_username and
                    appointment_date >= today and
                    row['status'] in ["pending", "confirmed"]
                ):
                    appointments.append(row)
            appointments.sort(key=lambda x: (x['date'], x['timeslot']))

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

def handle_manage_appointments(user):
    while True:
        print("\nManage Appointments:")
        print("1. View all appointments")
        print("2. Confirm an appointment")
        print("3. Cancel an appointment")
        print("4. Back to main menu")

        manage_choice = input("Select an option (1-4): ").strip()
        if manage_choice == "1":
            list_appointments_for_mhw(user.username)
        elif manage_choice in ["2", "3"]:
            manage_appointment_action(user, manage_choice)
        elif manage_choice == "4":
            break