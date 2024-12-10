import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
from utils.notification import send_email_notification, get_email_by_username
from config import *

def handle_modify_availibility(user, file_path=SCHEDULE_DATA_PATH): # choice 2, handle modify availability
    while True:
        print("\nModify Your Availability Options:")
        print("1. Take a Leave (Adjust availability for specific dates)")
        print("2. Change Time Slots for Specific Dates")
        print("3. Add Available Timeslot")
        print("4. Back to main menu")

        modify_choice = input("Select an option (1-3): ").strip()
        if modify_choice == '1':  # Take a Leave
            try:
                # Check if the schedule file exists
                if not os.path.exists(file_path):
                    print(f"Error: Schedule file '{file_path}' not found. Please set up your schedule first.")
                    continue

                # Load the schedule file
                schedule_df = pd.read_csv(file_path, encoding="utf-8")

                # Filter schedules for the current user (case-insensitive matching)
                user_schedule = schedule_df[schedule_df['mhwp_username'].str.lower() == user.username.lower()]

                # Check if the user has any schedule set
                if user_schedule.empty:
                    print("No available schedule found for your account. Please set up your availability.")
                    continue

                # Display the current schedule for the user
                print("\n--- Your Current Schedule ---")
                current_schedule = schedule_df[
                schedule_df['mhwp_username'].str.lower() == user.username.lower()]
                print(tabulate(current_schedule, headers="keys", tablefmt="grid"))

                # Prompt user for leave dates
                while True:
                    leave_dates = input(
                        "\nEnter the dates you want to take leave for (YYYY/MM/DD), separated by commas: ").strip()
                    leave_dates = [date.strip() for date in leave_dates.split(",")]

                    # Validate each date format
                    invalid_dates = []
                    for date in leave_dates:
                        try:
                            datetime.strptime(date, "%Y/%m/%d")
                        except ValueError:
                            invalid_dates.append(date)

                # Check if dates are within the schedule
                    unavailable_dates = [date for date in leave_dates if date not in user_schedule['Date'].values]

                    if invalid_dates:
                        print("\nThe following dates are invalid:")
                        for invalid_date in invalid_dates:
                            print(f"  {invalid_date} is invalid.Please enter dates in the format YYYY/MM/DD.")
                    elif unavailable_dates:
                        print("\nThe following dates are not within your schedule:")
                        for unavailable_date in unavailable_dates:
                            print(f"  {unavailable_date} is not within your current schedule range")
                    else:
                        break

                # Modify availability for the selected dates
                for date in leave_dates:
                    if date in user_schedule['Date'].values:
                        schedule_df.loc[
                            (schedule_df['mhwp_username'].str.lower() == user.username.lower()) &
                            (schedule_df['Date'] == date),
                            schedule_df.columns[3:]  # Adjust all time slots
                        ] = "□"  # Mark all time slots as unavailable

                # Save the updated schedule
                schedule_df.to_csv(file_path, index=False)
                print(
                    "\nYour availability has been updated. All available slots for the selected dates are now unavailable.")

            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.")
            except Exception as e:
                print(f"Error processing leave request: {str(e)}")


        elif modify_choice == '2':  # Change Time Slots
            try:
                if not os.path.exists(file_path):
                    print(f"Error: Schedule file '{file_path}' not found. Please set up your schedule first.")
                    continue
                # load file
                schedule_df = pd.read_csv(file_path, encoding="utf-8")
                #obtain current user's schedule
                user_schedule = schedule_df[schedule_df['mhwp_username'].str.lower() == user.username.lower()]
                # check if current user sets schedule
                if user_schedule.empty:
                    print("No available schedule found for your account. Please set up your availability first.")
                    continue

                print("\n--- Your Current Schedule ---")
                print(tabulate(user_schedule, headers="keys", tablefmt="grid"))

                # Prompt user to enter dates and validate
                while True:
                    modify_dates = input(
                        "\nEnter the dates you want to modify (YYYY/MM/DD), separated by commas: ").strip()
                    modify_dates = [date.strip() for date in modify_dates.split(",")]

                    # Validate date format
                    invalid_dates = []
                    for date in modify_dates:
                        try:
                            datetime.strptime(date, "%Y/%m/%d")
                        except ValueError:
                            invalid_dates.append(date)

                    # Check if dates are within the schedule
                    unavailable_dates = [date for date in modify_dates if date not in user_schedule['Date'].values]
                    if invalid_dates:
                        print("\nThe following dates are in an incorrect format:")
                        for invalid_date in invalid_dates:
                            print(f" -{invalid_date} is not in the format YYYY/MM/DD.")
                    elif unavailable_dates:
                        print("\nThe following dates are not within your schedule:")
                        for unavailable_date in unavailable_dates:
                            print(f"  {unavailable_date} is not within your schedule range")
                    else:
                        break

                updated_user_schedule = user_schedule.to_dict('records')
                num_slots = len(schedule_df.columns) - 3
                time_slots = schedule_df.columns[3:]
                for date in modify_dates:
                    matching_row = next((row for row in updated_user_schedule if row['Date'] == date), None)
                    if not matching_row:
                        print(f"\nNo schedule found for the date: {date}.")
                        continue

                    print(f"\nCurrent Time Slots for {date} ({matching_row['Day']}):")
                    print(tabulate(
                        [["Date"] + list(time_slots), [date] + [matching_row[slot] for slot in time_slots]],
                        headers="firstrow", tablefmt="grid"
                    ))

                    # modified time slot by current username
                    while True:
                        try:
                            current_index = int(input(
                                f"\nEnter the index of the currently available slot you want to move (e.g., 0-{num_slots - 1}): ").strip())
                            if 0 <= current_index < num_slots:
                                current_slot = time_slots[current_index]
                                if matching_row[current_slot] == "■":
                                    break
                                elif matching_row[current_slot] in ["▲", "●"]:
                                    print(
                                        f"\nThe current slot {time_slots[current_index]} cannot be modified due to the appointment.")
                                else:
                                    print("Invalid selection. Please choose a valid available slot (■).")
                            else:
                                print(f"Invalid index. Please enter a valid index between 0 and {num_slots - 1}.")
                        except ValueError:
                            print("Invalid input. Please enter a valid index as an integer.")
                    # target time slot
                    while True:
                        try:
                            target_index = int(input(
                                f"\nEnter the index of the target slot to make available (e.g., 0-{num_slots - 1}): ").strip())
                            if 0 <= target_index < num_slots:
                                target_slot = time_slots[target_index]
                                if matching_row[target_slot] == "□":
                                    break
                                elif matching_row[target_slot] in ["▲", "●"]:
                                    print(
                                        f"\nThe target slot {time_slots[target_index]} cannot be modified due to the appointment.")
                                else:
                                    print("Invalid selection. Please choose an unavailable slot (□).")
                            else:
                                print(f"Invalid index. Please enter a valid index between 0 and {num_slots - 1}.")
                        except ValueError:
                            print("Invalid input. Please enter a valid index as an integer.")
                    # swap
                    matching_row[current_slot], matching_row[target_slot] = "□", "■"
                # update time slots
                schedule_df.update(pd.DataFrame(updated_user_schedule))
                schedule_df.to_csv(file_path, index=False)
                print("\nYour updated time slots have been saved successfully!")
                print("\nUpdated Schedule (After Modifications):")
                updated_user_schedule_display = schedule_df[
                    schedule_df['mhwp_username'].str.lower() == user.username.lower()]
                print(tabulate(updated_user_schedule_display, headers="keys", tablefmt="grid"))
            except Exception as e:
                print(f"Error modifying time slots: {str(e)}")

        elif modify_choice == '3':  # Add Available Timeslot
            try:
                if not os.path.exists(file_path):
                    print(f"Error: Schedule file '{file_path}' not found. Please set up your schedule first.")
                    continue
                # Load the schedule file
                schedule_df = pd.read_csv(file_path, encoding="utf-8")

                # Obtain current user's schedule
                user_schedule = schedule_df[schedule_df['mhwp_username'].str.lower() == user.username.lower()]

                # Check if the user has any schedule set
                if user_schedule.empty:
                    print("No available schedule found for your account. Please set up your availability first.")
                    continue

                print("\n--- Your Current Schedule ---")
                print(tabulate(user_schedule, headers="keys", tablefmt="grid"))

                # Prompt user to enter a date and validate
                while True:
                    add_date = input("\nEnter the date you want to add an available timeslot for (YYYY/MM/DD): ").strip()

                    try:
                        datetime.strptime(add_date, "%Y/%m/%d")  # Validate format
                        if add_date not in user_schedule['Date'].values:
                            print(f"Date {add_date} is not within your current schedule range. Please try again.")
                        else:
                            break
                    except ValueError:
                        print("Invalid date format. Please enter a date in the format YYYY/MM/DD.")

                # Find the schedule row for the specified date
                matching_row = user_schedule[user_schedule['Date'] == add_date].iloc[0].to_dict()
                time_slots = schedule_df.columns[3:]
                print(f"\nCurrent Time Slots for {add_date} ({matching_row['Day']}):")
                print(tabulate(
                    [["Index"] + list(time_slots), ["Date"] + [matching_row[slot] for slot in time_slots]],
                    headers="firstrow", tablefmt="grid"
                ))

                # Select a timeslot to mark as available
                while True:
                    try:
                        target_index = int(input(
                            f"\nEnter the index of the timeslot to make available (e.g., 0-{len(time_slots) - 1}): ").strip())
                        if 0 <= target_index < len(time_slots):
                            target_slot = time_slots[target_index]
                            if matching_row[target_slot] == "■":
                                print(
                                    "\nInvalid selection. Timeslot is already available (■). Please select a different timeslot.")
                            elif matching_row[target_slot] in ["■", "▲", "●"]:
                                print(
                                    f"\nInvalid selection. Timeslot {time_slots[target_index]} cannot be modified. Please select a timeslot marked as □ (unavailable).")
                            else:
                                # Update the selected timeslot to available
                                schedule_df.loc[
                                    (schedule_df['mhwp_username'].str.lower() == user.username.lower()) &
                                    (schedule_df['Date'] == add_date),
                                    target_slot
                                ] = "■"
                                print(
                                    f"\nTimeslot {time_slots[target_index]} has been successfully marked as available.")
                                break
                        else:
                            print(f"Invalid index. Please enter a valid index between 0 and {len(time_slots) - 1}.")
                    except ValueError:
                        print("Invalid input. Please enter a valid index as an integer.")
                # Save the updated schedule
                schedule_df.to_csv(file_path, index=False)
                print("\nYour updated schedule has been saved successfully!")
                print("\nUpdated Schedule (After Modifications):")
                updated_user_schedule_display = schedule_df[
                    schedule_df['mhwp_username'].str.lower() == user.username.lower()]
                print(tabulate(updated_user_schedule_display, headers="keys", tablefmt="grid"))
            except Exception as e:
                print(f"Error adding available timeslot: {str(e)}")

        elif modify_choice == '4':  # Back to main menu
            break
        else:
            print("Invalid choice. Please select 1, 2, 3,4")
        