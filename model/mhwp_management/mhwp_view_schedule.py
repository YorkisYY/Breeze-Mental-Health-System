import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
from config import *

def display_upcoming_appointments(username, file_path=APPOINTMENTS_DATA_PATH):
    """
    Display the confirmed and pending appointments for the next week for the MHW, sorted by date and time.
    """
    if not os.path.exists(file_path):
        print(f"Error: Appointment file '{file_path}' not found.")
        return
    try:
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
        
        
def display_current_schedule(username, file_path=SCHEDULE_DATA_PATH):
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
            time_slots = [f"{hour}-{hour+1}{'am' if hour < 12 else 'pm'} ({i})" for i, hour in enumerate(range(set_start_hour, set_end_hour))]
            # Create display table
            headers = ["Date"] + ["Day"] +  time_slots
            
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

def handle_view_schedule(user): # choice 3, handle view schedule
    while True:
        print("\nSchedule and Appointment Management:")
        print("1. View schedule for the next month")
        print("2. View appointments for the next week")
        print("3. Back to main menu")

        schedule_choice = input("Select an option (1-3): ").strip()
        if schedule_choice == "1":  # View schedule for the next month
            display_current_schedule(user.username, file_path=SCHEDULE_DATA_PATH)
        elif schedule_choice == "2":  # View detailed appointments for the next week
            display_upcoming_appointments(user.username, file_path=APPOINTMENTS_DATA_PATH)
        elif schedule_choice == "3":  # Back to main menu
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please select a valid option.")