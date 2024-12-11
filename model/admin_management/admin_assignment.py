import os
import csv
from tabulate import tabulate
import random
from config import *
from model.user_account_management.user_data_manage import toggle_user_account_status
import pandas as pd
from utils.list_all_user import list_all_users
from services.summary import display_summary

MATCHING_RULES = {
    "Emotional Management": {"Anxiety", "Depression", "PTSD", "Bipolar Disorder"},
    "Behavioral Therapy": {"OCD", "ADHD", "Eating Disorder", "Substance Abuse"},
    "Severe Disorders": {"Schizophrenia", "Borderline Personality Disorder"},
    "General Wellbeing": {"Other/General Wellbeing"}
}

def get_patients_with_symptoms(PATIENTS_DATA_PATH=PATIENTS_DATA_PATH):
    """
    Get a dictionary of patients with their symptoms from patients.csv.
    """
    patients = {}
    if not os.path.exists(PATIENTS_DATA_PATH):
        print(f"Error: Patient data file '{PATIENTS_DATA_PATH}' not found.")
        return patients

    try:
        with open(PATIENTS_DATA_PATH, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                patients[row["username"]] = row["symptoms"]
    except Exception as e:
        print(f"Error reading patient data: {str(e)}")
    return patients

def get_mhwps_with_major(mhwp_data_path=MHWP_DATA_PATH):
    """
    Get a dictionary of MHWPs with their major from mhwp.csv.
    """
    mhwps = {}
    if not os.path.exists(mhwp_data_path):
        print(f"Error: MHWP data file '{mhwp_data_path}' not found.")
        return mhwps

    try:
        with open(mhwp_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                mhwps[row["username"]] = row["major"]
    except Exception as e:
        print(f"Error reading MHWP data: {str(e)}")
    return mhwps

def get_current_assignments(assignments_path="data/assignments.csv"):
    """
    Load current assignments from assignments.csv.
    """
    assignments = {}
    if os.path.exists(assignments_path):
        with open(assignments_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                mhwp_username = row["mhwp_username"]
                patient_username = row["patient_username"]
                if mhwp_username not in assignments:
                    assignments[mhwp_username] = []
                assignments[mhwp_username].append(patient_username)
    return assignments

def update_mhwp_csv_with_assignments(assignments_path=ASSIGNMENTS_DATA_PATH, mhwp_data_path=MHWP_DATA_PATH):
    """
    Update the `assigned_patients` column in mhwp.csv based on the assignments.
    """
    # Load current assignments
    current_assignments = get_current_assignments(assignments_path)

    # Load MHWP data
    if not os.path.exists(mhwp_data_path):
        print(f"Error: MHWP data file '{mhwp_data_path}' not found.")
        return

    try:
        with open(mhwp_data_path, "r", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
            
        # Update assigned_patients for each MHWP
        for row in rows:
            username = row["username"]
            if username in current_assignments:
                # Convert to set to remove duplicates
                assigned_patients = set(current_assignments[username])
                row["assigned_patients"] = ",".join(assigned_patients)
            else:
                row["assigned_patients"] = ""

        # Save updated MHWP data
        with open(mhwp_data_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("Updated `assigned_patients` in MHWP data.")
    except Exception as e:
        print(f"Error processing MHWP data: {str(e)}")

def update_patients_csv_with_assignments(assignments_path=ASSIGNMENTS_DATA_PATH, patient_data_path=PATIENTS_DATA_PATH):
    """
    Update the `assigned_mhwp` column in patients.csv based on the assignments.
    """
    # Load current assignments
    current_assignments = get_current_assignments(assignments_path)

    # Create patient to MHWP mapping
    patient_to_mhwp = {patient: mhwp for mhwp, patients in current_assignments.items() for patient in patients}

    # Load patient data
    if not os.path.exists(patient_data_path):
        print(f"Error: Patient data file '{patient_data_path}' not found.")
        return

    try:
        with open(patient_data_path, "r", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        # Update assigned_mhwp for each patient
        for row in rows:
            username = row["username"]
            row["assigned_mhwp"] = patient_to_mhwp.get(username, "")

        # Save updated patient data
        with open(patient_data_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("Updated `assigned_mhwp` in patient data.")
    except Exception as e:
        print(f"Error processing patient data: {str(e)}")

def save_assignments(assignments, assignments_path=ASSIGNMENTS_DATA_PATH):
    """
    Save assignments to assignments.csv.
    """
    # Convert to set of tuples to remove duplicates
    unique_assignments = {(patient, mhwp) 
                        for mhwp, patients in assignments.items() 
                        for patient in set(patients)}
    
    # Convert back to list for writing
    table_data = sorted(list(unique_assignments))

    with open(assignments_path, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["patient_username", "mhwp_username"])
        writer.writerows(table_data)

    print("\nUpdated Assignments:")
    print(tabulate(table_data, headers=["Patient Username", "MHWP Username"], tablefmt="grid"))


def display_assignments(assignments_path=ASSIGNMENTS_DATA_PATH):
    """
    Display all current assignments in a table format.
    """
    current_assignments = get_current_assignments(assignments_path)
    table_data = [{"Patient Username": patient, "MHWP Username": mhwp}
                  for mhwp, patients in current_assignments.items() for patient in patients]

    print("\nCurrent Assignments:")
    if table_data:
        print(tabulate(table_data, headers="keys", tablefmt="grid"))
    else:
        print("No assignments found.")
        
def get_mhwps_with_schedule(schedule_path="data/mhwp_schedule.csv"):
    """
    Get a list of MHWPs that have an available schedule in mhwp_schedule.csv.
    """
    mhwps_with_schedule = set()
    if not os.path.exists(schedule_path):
        print(f"Error: Schedule file '{schedule_path}' not found.")
        return mhwps_with_schedule

    try:
        with open(schedule_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["mhwp_username"] and any(value == "□" for value in row.values()):
                    mhwps_with_schedule.add(row["mhwp_username"])
    except Exception as e:
        print(f"Error reading schedule: {str(e)}")

    return mhwps_with_schedule

def modify_assignments(assignments_path=ASSIGNMENTS_DATA_PATH,
                       patient_data_path=PATIENTS_DATA_PATH,
                       mhwp_data_path=MHWP_DATA_PATH,
                       schedule_path=SCHEDULE_DATA_PATH):
    """
    Modify the existing assignments in the assignments file or assign unassigned users.
    """
    current_assignments = get_current_assignments(assignments_path)
    if not current_assignments or all(len(patients) == 0 for patients in current_assignments.values()):
        print("No existing assignments found. Please complete the initial assignment first.")
        return
    display_assignments(assignments_path)

    print("\nModify Assignments Options:")
    print("1. Modify an existing assignment")
    print("2. Assign unassigned patients and MHWPs")

    choice = input("\nEnter your choice (1-2): ").strip()

    if choice == '1':  # Modify an existing assignment
        patient_to_modify = input("\nEnter the patient username to modify assignment: ").strip()
        # Read patient data to find symptoms
        patients_with_symptoms = get_patients_with_symptoms(patient_data_path)
        if patient_to_modify not in patients_with_symptoms:
            print(f"Patient '{patient_to_modify}' not found in the records.")
            return

        symptom = patients_with_symptoms[patient_to_modify]
        print(f"Patient '{patient_to_modify}' has the symptom: {symptom}")

        # Find eligible MHWPs based on matching rules
        eligible_mhwps = [
            mhwp for mhwp, major in get_mhwps_with_major(mhwp_data_path).items()
            if symptom in MATCHING_RULES.get(major, set())
        ]

        if not eligible_mhwps:
            print(f"No eligible MHWPs found for symptom '{symptom}'.")
            return

        print("\nEligible MHWPs:")
        for mhwp in eligible_mhwps:
            print(f"- {mhwp}")

        # Let the user select a new MHWP
        new_mhwp = input("\nEnter the new MHWP username for this patient: ").strip()
        if new_mhwp not in eligible_mhwps:
            print(f"'{new_mhwp}' is not a valid choice. Please choose from the eligible MHWPs.")
            return

        # Update assignments
        for mhwp, patients in current_assignments.items():
            if patient_to_modify in patients:
                patients.remove(patient_to_modify)
                break

        current_assignments.setdefault(new_mhwp, []).append(patient_to_modify)
        save_assignments(current_assignments, assignments_path)
        update_mhwp_csv_with_assignments(assignments_path, mhwp_data_path)
        update_patients_csv_with_assignments(assignments_path, patient_data_path)
        print(f"\nPatient '{patient_to_modify}' has been reassigned to MHWP '{new_mhwp}'.")

    elif choice == '2':  # Reassign for unassigned patients and MHWPs
        # Load necessary data
        current_assignments = get_current_assignments(assignments_path)
        all_patients = set(get_patients_with_symptoms(patient_data_path).keys())
        assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
        unassigned_patients = list(all_patients - assigned_patients)
        all_mhwps = set(get_mhwps_with_major(mhwp_data_path).keys())
        mhwps_with_schedule = get_mhwps_with_schedule(schedule_path)
        unassigned_mhwps = all_mhwps - set(current_assignments.keys())
        # Filter unassigned MHWPs
        unassigned_mhwps_with_schedule = unassigned_mhwps & mhwps_with_schedule
        unassigned_mhwps_without_schedule = unassigned_mhwps - mhwps_with_schedule
        # Notify about unassigned MHWPs without schedule
        if unassigned_mhwps_without_schedule:
            print("\n--- Unassigned MHWPs with no available schedule ---")
            mhwp_table = [{"MHWP Username": mhwp, "Status": "No Schedule"} for mhwp in unassigned_mhwps_without_schedule]
            print(tabulate(mhwp_table, headers="keys", tablefmt="grid"))
        # Assign unassigned patients to MHWPs with schedules
        if unassigned_patients:
            print("\n--- Assigning unassigned patients to available MHWPs ---")
            patients_with_symptoms = get_patients_with_symptoms(patient_data_path)
            mhwps_with_major = get_mhwps_with_major(mhwp_data_path)
            for patient in list(unassigned_patients):
                symptom = patients_with_symptoms.get(patient)
                if not symptom:
                    print(f"No symptom found for patient '{patient}'. Skipping.")
                    continue
                # Find eligible MHWPs for the patient
                eligible_mhwps = [
                    mhwp for mhwp in unassigned_mhwps_with_schedule
                    if symptom in MATCHING_RULES.get(mhwps_with_major.get(mhwp, ""), set())
                ]
                if eligible_mhwps:
                    # Assign patient to an unassigned MHWP
                    selected_mhwp = random.choice(eligible_mhwps)
                    current_assignments.setdefault(selected_mhwp, []).append(patient)
                    unassigned_patients.remove(patient)
                    print(f"Assigned: Patient '{patient}' -> MHWP '{selected_mhwp}'")
                else:
                    print(f"Patient '{patient}' cannot be assigned due to no eligible MHWP with a schedule.")
        else:
            print("\nNo unassigned patients to process.")

        # Save the results and update related files
        save_assignments(current_assignments, assignments_path)
        update_mhwp_csv_with_assignments(assignments_path=assignments_path, mhwp_data_path=mhwp_data_path)
        update_patients_csv_with_assignments(assignments_path=assignments_path, patient_data_path=patient_data_path)
        print("\n--- Assignments Updated ---")
    else:
        print("\nInvalid choice. Returning to menu.")
        return