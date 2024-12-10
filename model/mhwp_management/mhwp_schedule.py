import os
import csv
import calendar
import pandas as pd
from tabulate import tabulate
from os.path import exists
import pandas as pd
from datetime import datetime, timedelta
from . import *
from config import *
from .mhwp_appointment import *
from .mhwp_view_schedule import *   
from .mhwp_availability import *

def update_mhwp_schedules(schedule_file=SCHEDULE_DATA_PATH, template_file=MHWP_SCHEDULE_TEMPLATE_PATH, silent=False):
    today = datetime.now()
    week_starts = [
        today,  # Current week
        today + timedelta(weeks=1),  # Next week 
        today + timedelta(weeks=2),  # Week 3
        today + timedelta(weeks=3)   # Week 4
    ]
    
    # Read templates first
    templates_df = pd.read_csv(template_file)
    mhwp_users = templates_df['mhwp_username'].unique()
    # Read existing schedules and clean past entries
    existing_schedules = pd.DataFrame()
    if os.path.exists(schedule_file):
        existing_schedules = pd.read_csv(schedule_file)
        existing_schedules['Date'] = pd.to_datetime(existing_schedules['Date'])
        yesterday = today - timedelta(days=1)
        existing_schedules = existing_schedules[existing_schedules['Date'] > yesterday]    
    new_schedules = []
    
    for mhwp in mhwp_users:
        # Check if MHWP has existing schedule
        if not existing_schedules.empty:
            mhwp_schedule = existing_schedules[existing_schedules['mhwp_username'] == mhwp].copy()
        else:
            mhwp_schedule = pd.DataFrame()
        
        if mhwp_schedule.empty:
            # Generate full 4 weeks
            start_date = today
            end_date = week_starts[3] + timedelta(days=7)
        else:
            # Convert dates for comparison using loc
            mhwp_schedule.loc[:, 'Date'] = pd.to_datetime(mhwp_schedule['Date'], format='%Y/%m/%d')
            
            # Keep first 2 weeks only
            keep_schedules = mhwp_schedule[mhwp_schedule['Date'] < week_starts[2]]
            if not keep_schedules.empty:
                new_schedules.extend(keep_schedules.to_dict('records'))            
            # Check weeks 3-4 for appointments
            for week_num in [2, 3]:
                week_schedule = mhwp_schedule[
                    (mhwp_schedule['Date'] >= week_starts[week_num]) & 
                    (mhwp_schedule['Date'] < (week_starts[week_num] + timedelta(days=7)))
                ]
                
                if not week_schedule.empty:
                    has_appointments = week_schedule.iloc[:, 3:].isin(["●"]).any().any()
                    if has_appointments:
                        if not silent:
                            print(f"\nWarning: Detected confirmed appointments for {mhwp} in Week {week_num + 1}")
                            print(f"Please cancel appointments for {week_starts[week_num].strftime('%Y/%m/%d')} - {(week_starts[week_num] + timedelta(days=6)).strftime('%Y/%m/%d')}")
                        return False
            
            # Update weeks 3-4
            start_date = week_starts[2] + timedelta(days=1)
            end_date = week_starts[3] + timedelta(days=7)
        
        # Generate new schedules for this MHWP
        mhwp_templates = templates_df[templates_df['mhwp_username'] == mhwp].to_dict('records')
        current_date = start_date
        while current_date < end_date:
            # Find matching template for current weekday
            day_template = next((t for t in mhwp_templates if int(t['weekday']) == current_date.weekday()), None)
            if day_template:
                schedule_entry = {
                    'mhwp_username': mhwp,
                    'Date': current_date.strftime("%Y/%m/%d"),
                    'Day': current_date.strftime("%A")
                }
                for col in templates_df.columns:
                    if '(' in col:
                        schedule_entry[col] = day_template[col]
                new_schedules.append(schedule_entry)
            current_date += timedelta(days=1)
    
    # Convert to DataFrame, sort by username and date
    final_schedules = pd.DataFrame(new_schedules)
    final_schedules['Date'] = pd.to_datetime(final_schedules['Date'])
    
    # Sort by username first, then date
    final_schedules = final_schedules.sort_values(['mhwp_username', 'Date'])
    
    # Keep last occurrence when dropping duplicates
    final_schedules = final_schedules.drop_duplicates(
        subset=['mhwp_username', 'Date'], 
        keep='last'
    )
    
    # Format date back to string
    final_schedules['Date'] = final_schedules['Date'].dt.strftime('%Y/%m/%d')

    # Save sorted schedules
    final_schedules.to_csv(schedule_file, index=False)
    if not silent:
        print("\nSchedule updated successfully!")
    return True

    
def setup_mhwp_schedule_template(user, file_path=MHWP_SCHEDULE_TEMPLATE_PATH):
    # Read existing templates if any
    existing_templates = []
    if os.path.exists(file_path):
        templates_df = pd.read_csv(file_path)
        # Keep other MHWPs' templates
        existing_templates = templates_df[templates_df['mhwp_username'] != user.username].to_dict('records')

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

    # Process each weekday
    for day in range(7):
        # Display current template
        print("\nCurrent Schedule Template:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print("Legend: ■=Available, □=Unavailable")
        # Show time slot reference 
        print("Time Slot:")
        print(time_slots)
        
        print(f"\nSelect time slots for {weekdays[day]}")
        print("Options:")
        print("- Enter slot numbers separated by commas (e.g. 0,1,2)")
        print("- Enter 'r' to discard changes and return to previous menu")
        print("- Enter '-' to leave all slots unavailable") 
        print("- Enter '+' to select all slots")
        print("- Press Enter to copy previous day's slots")
        
        while True:
            choice = input("> ").strip().lower()
            
            if choice == "r":  # Return to previous menu
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
            'mhwp_username': user.username,
            'weekday': day
        }
        # Add time slots as individual columns instead of dictionary
        for i, slot in enumerate(storage_time_slots):
            template[slot] = rows[day][i+1]
        templates.append(template)

    # Show final template
    print("\nFinal Schedule Template:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Add existing templates after creating new ones
    templates.extend(existing_templates)
    
    # Save all templates
    template_df = pd.DataFrame(templates)
    template_df.to_csv(file_path, index=False)


def handle_set_schedule(user):
    print("\nSchedule Management Options:")
    print("1. Set up your schedule template")
    print("2. Modify your availability")
    print("3. View your current schedule")

    schedule_choice = input("Select an option (1-3): ").strip()

    if schedule_choice == '1':
        setup_mhwp_schedule_template(user)
        update_mhwp_schedules() # Update mhwp schedules after template is set
    elif schedule_choice == '2':
        handle_modify_availibility(user)
    elif schedule_choice == '3':
        handle_view_schedule(user)
    else:
        print("Invalid choice. Please select a valid option.")
        
    # if schedule_choice == '1':
    #     setup_mhwp_schedule(user) # no longer use this function to set schedule
    # elif schedule_choice == '2':
    #     handle_modify_availibility(user)
    # elif schedule_choice == '3':
    #     handle_view_schedule(user)
    # elif schedule_choice == '4':
    #     setup_mhwp_schedule_template(user)
    #     update_mhwp_schedules() # Update mhwp schedules after template is set
    # else:
    #     print("Invalid choice. Please select a valid option.")
        