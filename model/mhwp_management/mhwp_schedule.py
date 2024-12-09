import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
from mhwp_management import *
from config import *

def modify_mhwp_schedule(user, option, dates=None, time_slot_indices=None,file_path=SCHEDULE_DATA_PATH):
    if not os.path.exists(file_path):
        print(f"Error: Schedule file '{file_path}' not found.")
        return
    try:
        with open(file_path, "r", encoding="utf-8") as file:
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
        with open(file_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers
            writer.writerows(updated_schedules)  # Write all data
    except Exception as e:
        print(f"Error modifying schedule: {str(e)}")







def update_mhwp_schedules(schedule_file=SCHEDULE_DATA_PATH, template_file=MHWP_SCHEDULE_TEMPLATE_PATH):
    """Updates MHWP schedules while preserving appointments"""
    
    # Calculate date ranges
    today = datetime.now()
    two_weeks_later = today + timedelta(weeks=2)
    end_date = today + timedelta(weeks=4)

    # Read existing schedules
    if os.path.exists(schedule_file):
        # existing_schedules = pd.read_csv(schedule_file)
        # existing_schedules['Date'] = pd.to_datetime(existing_schedules['Date'])

        existing_schedules = pd.read_csv(schedule_file)
        # Specify the format when converting to datetime
        existing_schedules['Date'] = pd.to_datetime(existing_schedules['Date'], format='%Y/%m/%d')
        
        # Keep current and next week's schedules
        keep_schedules = existing_schedules[existing_schedules['Date'] < two_weeks_later]
        
        # Check for appointments in weeks 3-4
        future_schedules = existing_schedules[
            (existing_schedules['Date'] >= two_weeks_later) & 
            (existing_schedules['Date'] <= end_date)
        ]
        
        has_appointments = future_schedules.iloc[:, 3:].isin(["●"]).any().any()
        if has_appointments:
            print("Warning: Detected confirmed appointments in weeks 3-4.")
            print("Please cancel appointments before updating schedule.")
            return False
    
    # Generate new schedules for weeks 3-4
    templates_df = pd.read_csv(template_file)
    templates = templates_df.to_dict('records')
    new_schedules = []
    
    for template in templates:
        current_date = two_weeks_later
        while current_date <= end_date:
            if current_date.weekday() == int(template['weekday']):
                schedule_entry = {
                    'mhwp_username': template['mhwp_username'],
                    'Date': current_date.strftime("%Y/%m/%d"),
                    'Day': current_date.strftime("%A")
                }
                for col in templates_df.columns:
                    if '(' in col:
                        schedule_entry[col] = template[col]
                new_schedules.append(schedule_entry)
            current_date += timedelta(days=1)

    # Combine and save
    new_schedules_df = pd.DataFrame(new_schedules)
    if 'keep_schedules' in locals():
        final_schedules = pd.concat([keep_schedules, new_schedules_df])
    else:
        final_schedules = new_schedules_df
        
    final_schedules.to_csv(schedule_file, index=False)
    return True


        

        
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
        
        

            
            
def setup_mhwp_schedule_template(user, file_path="data/mhwp_schedule_template.csv"): 
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    storage_time_slots = generate_time_slots(set_start_hour, set_end_hour)
    time_slots = [f"{hour}-{hour+1}{'am' if hour < 12 else 'pm'} ({i})" for i, hour in enumerate(range(set_start_hour, set_end_hour))]
    templates = []
    prev_slots = None

    # Create display table
    headers = ["Day"] + time_slots
    rows = []
    for day in weekdays:
        row = [day] + ["□" for _ in time_slots]
        rows.append(row)

    # Show time slot reference separately
    print("\nTime Slot Reference:")
    for idx, slot in enumerate(time_slots):
        print(f"{idx}: {slot}")
        
    # Process each weekday
    for day in range(7):
        # Display current template
        print("\nCurrent Schedule Template:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print("\nLegend: ■=Available, □=Unavailable")
        
        print(f"\nSelect time slots for {weekdays[day]}")
        print("Options:")
        print("- Enter slot numbers separated by commas (e.g. 0,1,2)")
        print("- Enter 'r' to discard changes and return to previous menu")
        print("- Enter '-' to leave all slots unavailable") 
        print("- Enter '+' to select all slots")
        print("- Press Enter to copy previous day's slots")
        
        while True:
            
            choice = input("> ").strip().lower()  # Convert to lowercase
            
            if choice == "r":  # All slots unavailable
                return
            
            if choice == "-":  # All slots unavailable
                for i in range(1, len(time_slots)+1):
                    rows[day][i] = "□"
                prev_slots = ["□" for _ in time_slots]
                break
            elif choice == "+":  # All slots available
                for i in range(1, len(time_slots)+1):
                    rows[day][i] = "■"
                prev_slots = ["■" for _ in time_slots]
                break
            elif not choice and prev_slots and day > 0:  # Copy previous day
                for i in range(1, len(time_slots)+1):
                    rows[day][i] = prev_slots[i-1]
                break
            elif not choice and day == 0:  # First day can't copy
                print("Cannot copy previous day's slots on first day")
                continue
            else:  # Specific slots
                try:
                    indices = [int(idx) for idx in choice.split(",") if idx.strip()]
                    if all(0 <= idx < len(time_slots) for idx in indices):
                        for i in range(1, len(time_slots)+1):
                            rows[day][i] = "■" if i-1 in indices else "□"
                        prev_slots = rows[day][1:]
                        break
                    else:
                        print(f"Error: Indices must be between 0 and {len(time_slots)-1}")
                except ValueError:
                    print("Invalid input. Please enter numbers separated by commas, or -, +, or Enter")

        # Store template for this day
        template = {
            "mhwp_username": user.username,
            "weekday": day,
            "time_slots": {slot: rows[day][i+1] for i, slot in enumerate(storage_time_slots)}  # Use storage format
        }
        templates.append(template)

        if len(templates) == 7:  # All days processed
            break

    # Show final template
    print("\nFinal Schedule Template:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Save template
    save_schedule_template(templates, file_path)

    
def save_schedule_template(templates, file_path=MHWP_SCHEDULE_TEMPLATE_PATH):
    """Saves MHWP weekly schedule template to CSV"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        template_rows = []
        for template in templates:
            row = {
                'mhwp_username': template['mhwp_username'],
                'weekday': template['weekday']
            }
            row.update(template['time_slots'])
            template_rows.append(row)
            
        template_df = pd.DataFrame(template_rows)
        template_df.to_csv(file_path, index=False)
        print("Schedule template saved successfully!")
        return True
        
    except Exception as e:
        print(f"Error saving schedule template: {e}")
        return False
    
    
def handle_set_schedule(user):
    print("\nSchedule Management Options:")
    print("1. Set up your availability")
    print("2. Modify your availability")
    print("3. View your current schedule")
    print("4. Modify your schedule template")

    schedule_choice = input("Select an option (1-3): ").strip()

    if schedule_choice == '1':
        setup_mhwp_schedule(user)
    elif schedule_choice == '2':
        handle_modify_availibility(user)
    elif schedule_choice == '3':
        handle_view_schedule(user)
    elif schedule_choice == '4':
        setup_mhwp_schedule_template(user)
        update_mhwp_schedules() # Update mhwp schedules after template is set
    else:
        print("Invalid choice. Please select a valid option.")
        