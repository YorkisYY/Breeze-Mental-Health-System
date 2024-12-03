import os
import csv
from tabulate import tabulate
import random
from config import USER_DATA_PATH
from config import PATIENTS_DATA_PATH
from config import MHWP_DATA_PATH

MATCHING_RULES = {
    "Emotional Management": {"Anxiety", "Depression", "PTSD", "Bipolar Disorder"},
    "Behavioral Therapy": {"OCD", "ADHD", "Eating Disorder", "Substance Abuse"},
    "Severe Disorders": {"Schizophrenia", "Borderline Personality Disorder"},
    "General Wellbeing": {"Other/General Wellbeing"}
}
def get_patients_with_symptoms(PATIENTS_DATA_PATH="data/patients.csv"):
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

def get_mhwps_with_major(mhwp_data_path="data/mhwp.csv"):
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

def update_mhwp_csv_with_assignments(assignments_path="data/assignments.csv", mhwp_data_path="data/mhwp.csv"):
    """
    Update the `assigned_patients` column in mhwp.csv based on the assignments.
    """
    # Load current assignments
    current_assignments = get_current_assignments(assignments_path)

    # Load MHWP data
    mhwps = []
    if not os.path.exists(mhwp_data_path):
        print(f"Error: MHWP data file '{mhwp_data_path}' not found.")
        return

    try:
        with open(mhwp_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            mhwps = [row for row in reader]
    except Exception as e:
        print(f"Error reading MHWP data: {str(e)}")
        return

    # Update `assigned_patients` for each MHWP
    for mhwp in mhwps:
        mhwp_username = mhwp["username"]
        if mhwp_username in current_assignments:
            mhwp["assigned_patients"] = ",".join(current_assignments[mhwp_username])
        else:
            mhwp["assigned_patients"] = ""

    # Save updated MHWP data
    try:
        with open(mhwp_data_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=mhwps[0].keys())
            writer.writeheader()
            writer.writerows(mhwps)
        print("Updated `assigned_patients` in MHWP data.")
    except Exception as e:
        print(f"Error writing to MHWP data: {str(e)}")

def update_patients_csv_with_assignments(assignments_path="data/assignments.csv", patient_data_path="data/patients.csv"):
    """
    Update the `assigned_mhwp` column in patients.csv based on the assignments.
    """
    # Load current assignments
    current_assignments = get_current_assignments(assignments_path)

    # Reverse the assignments to map patient -> MHWP
    patient_to_mhwp = {patient: mhwp for mhwp, patients in current_assignments.items() for patient in patients}

    # Load patient data
    patients = []
    if not os.path.exists(patient_data_path):
        print(f"Error: Patient data file '{patient_data_path}' not found.")
        return

    try:
        with open(patient_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            patients = [row for row in reader]
    except Exception as e:
        print(f"Error reading patient data: {str(e)}")
        return

    # Update `assigned_mhwp` for each patient
    for patient in patients:
        patient_username = patient["username"]
        if patient_username in patient_to_mhwp:
            patient["assigned_mhwp"] = patient_to_mhwp[patient_username]
        else:
            patient["assigned_mhwp"] = ""

    # Save updated patient data
    try:
        with open(patient_data_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=patients[0].keys())
            writer.writeheader()
            writer.writerows(patients)
        print("Updated `assigned_mhwp` in patient data.")
    except Exception as e:
        print(f"Error writing to patient data: {str(e)}")

def initialize_mhwp_schedule(schedule_path="data/mhwp_schedule.csv"):
    """
    Clear all data in the mhwp_schedule.csv file and keep only the column headers.
    """
    try:
        with open(schedule_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "mhwp_username", "Date", "Day",
                "09:00-10:00 (0)", "10:00-11:00 (1)", "11:00-12:00 (2)",
                "12:00-13:00 (3)", "13:00-14:00 (4)", "14:00-15:00 (5)",
                "15:00-16:00 (6)"
            ])
        print("\nMHWP schedule file has been initialized. All data cleared except headers.")
    except Exception as e:
        print(f"Error initializing MHWP schedule data: {str(e)}")



def initialize_user_data(user_data_path="data/user_data.csv"):
    """
    Clear all data in the user_data.csv file and keep only the column headers.
    """
    try:
        with open(user_data_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password", "email", "emergency_email", "role"])  # Write headers only
        print("\nUser data file has been initialized. All data cleared except headers.")
    except Exception as e:
        print(f"Error initializing user data: {str(e)}")

def initialize_assignments(assignments_path="data/assignments.csv"):
    """
    Clear all data in the assignments.csv file and keep only the column headers.
    """
    try:
        with open(assignments_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["patient_username", "mhwp_username"])  # Write headers only
        print("\nAssignments file has been initialized. All data cleared.")
    except Exception as e:
        print(f"Error initializing assignments: {str(e)}")


def get_patients(patient_data_path="data/patients.csv"):
    """
    Get a list of patient usernames from patients.csv.
    """
    patients = []
    if not os.path.exists(patient_data_path):
        print(f"Error: Patient data file '{patient_data_path}' not found.")
        return patients

    try:
        with open(patient_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                patients.append(row["username"])
    except Exception as e:
        print(f"Error reading patient data: {str(e)}")
    return patients

def get_mhwps(mhwp_data_path="data/mhwp.csv"):
    """
    Get a list of MHWP usernames from mhwp.csv.
    """
    mhwps = []
    if not os.path.exists(mhwp_data_path):
        print(f"Error: MHWP data file '{mhwp_data_path}' not found.")
        return mhwps

    try:
        with open(mhwp_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                mhwps.append(row["username"])
    except Exception as e:
        print(f"Error reading MHWP data: {str(e)}")
    return mhwps


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


def save_assignments(assignments, assignments_path="data/assignments.csv"):
    """
    Save assignments to assignments.csv.
    """
    table_data = []
    for mhwp, patients in assignments.items():
        for patient in patients:
            table_data.append([patient, mhwp])

    with open(assignments_path, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["patient_username", "mhwp_username"])
        writer.writerows(table_data)

    print("\nUpdated Assignments:")
    print(tabulate(table_data, headers=["Patient Username", "MHWP Username"], tablefmt="grid"))


def balanced_assign_patients_and_mhwps(patient_data_path="data/patients.csv",
                                       mhwp_data_path="data/mhwp.csv",
                                       assignments_path="data/assignments.csv",
                                       schedule_path="data/mhwp_schedule.csv"):
    """
    Assign patients to MHWPs in a balanced way, prioritizing unassigned MHWPs and matching symptoms to majors.
    """
    # Load necessary data
    eligible_mhwps = get_mhwps_with_schedule(schedule_path)
    patients_with_symptoms = get_patients_with_symptoms(patient_data_path)
    mhwps_with_major = get_mhwps_with_major(mhwp_data_path)
    current_assignments = get_current_assignments(assignments_path)

    # Initialize assignments dictionary
    assignments = {mhwp: patients.copy() for mhwp, patients in current_assignments.items()}
    assigned_mhwp_tracker = {mhwp: False for mhwp in eligible_mhwps}

    # Assign patients to MHWPs based on symptoms and major
    for patient, symptom in patients_with_symptoms.items():
        # Find eligible MHWPs based on major and symptom
        eligible_mhwps_for_patient = [
            mhwp for mhwp, major in mhwps_with_major.items()
            if mhwp in eligible_mhwps and symptom in MATCHING_RULES.get(major, set())
        ]

        if eligible_mhwps_for_patient:
            # Separate MHWPs into those who haven't been assigned and those who have
            unassigned_mhwps = [mhwp for mhwp in eligible_mhwps_for_patient if not assigned_mhwp_tracker[mhwp]]

            if unassigned_mhwps:
                # Assign to one of the unassigned MHWPs
                selected_mhwp = random.choice(unassigned_mhwps)
                assigned_mhwp_tracker[selected_mhwp] = True
            else:
                # All MHWPs have been assigned at least once, assign randomly
                selected_mhwp = random.choice(eligible_mhwps_for_patient)

            # Add patient to the selected MHWP
            assignments.setdefault(selected_mhwp, []).append(patient)
            print(f"Assigned: Patient '{patient}' -> MHWP '{selected_mhwp}' (Major: {mhwps_with_major[selected_mhwp]})")
        else:
            print(f"No eligible MHWP found for patient '{patient}' with symptom '{symptom}'.")

    # Save updated assignments
    save_assignments(assignments, assignments_path)
    # Update `mhwp.csv` 'patients.csv' with assigned patients and assigned mhwp
    update_mhwp_csv_with_assignments(assignments_path=assignments_path, mhwp_data_path=mhwp_data_path)
    update_patients_csv_with_assignments(assignments_path=assignments_path, patient_data_path=patient_data_path)


def modify_assignments(assignments_path="data/assignments.csv",
                       patient_data_path="data/patients.csv",
                       mhwp_data_path="data/mhwp.csv",
                       schedule_path="data/mhwp_schedule.csv"):
    """
    Modify the existing assignments in the assignments file or assign unassigned users.
    """
    current_assignments = get_current_assignments(assignments_path)
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

        # Save updated assignments
        save_assignments(current_assignments, assignments_path)

        # Update MHWP and patient CSVs
        update_mhwp_csv_with_assignments(assignments_path, mhwp_data_path)
        update_patients_csv_with_assignments(assignments_path, patient_data_path)

        print(f"\nPatient '{patient_to_modify}' has been reassigned to MHWP '{new_mhwp}'.")

    elif choice == '2':  # Reassign for unassigned patients and MHWPs
        print("\n--- Assigning unassigned patients and MHWPs ---")

        # Load necessary data
        current_assignments = get_current_assignments(assignments_path)
        all_patients = set(get_patients(patient_data_path))
        assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
        unassigned_patients = list(all_patients - assigned_patients)

        all_mhwps = set(get_mhwps(mhwp_data_path))
        mhwps_with_schedule = get_mhwps_with_schedule(schedule_path)
        unassigned_mhwps = set(all_mhwps - set(current_assignments.keys()))

        patients_with_symptoms = get_patients_with_symptoms(patient_data_path)
        mhwps_with_major = get_mhwps_with_major(mhwp_data_path)

        # No unassigned patients and MHWPs without schedules
        if not unassigned_patients and set(unassigned_mhwps) - mhwps_with_schedule:
            print("\n--- Unassigned MHWPs with no available schedule ---")
            mhwp_table = [{"MHWP Username": mhwp, "Status": "No Schedule"} for mhwp in
                          (set(unassigned_mhwps)  - mhwps_with_schedule)]
            print(tabulate(mhwp_table, headers="keys", tablefmt="grid"))

        #  No unassigned patients and MHWPs with available schedules
        elif not unassigned_patients and set(unassigned_mhwps) & mhwps_with_schedule:
            print("\n--- Unassigned MHWPs with available schedule ---")
            unassigned_and_available_mhwps = set(unassigned_mhwps)  & mhwps_with_schedule
            mhwp_table = [{"MHWP Username": mhwp} for mhwp in unassigned_and_available_mhwps]
            print(tabulate(mhwp_table, headers="keys", tablefmt="grid"))

        # Unassigned patients and unassigned MHWPs with available schedules
        elif unassigned_patients and unassigned_mhwps & mhwps_with_schedule:
            print("\n--- Assigning unassigned patients to available MHWPs ---")
            for patient in list(unassigned_patients):
                symptom = patients_with_symptoms.get(patient)
                if not symptom:
                    print(f"No symptom found for patient '{patient}'. Skipping.")
                    continue

                eligible_mhwps = [
                    mhwp for mhwp in (unassigned_mhwps & mhwps_with_schedule)
                    if symptom in MATCHING_RULES.get(mhwps_with_major.get(mhwp, ""), set())
                ]

                if eligible_mhwps:
                    selected_mhwp = random.choice(eligible_mhwps)
                    current_assignments.setdefault(selected_mhwp, []).append(patient)
                    unassigned_patients.remove(patient)
                    print(f"Assigned: Patient '{patient}' -> MHWP '{selected_mhwp}'")
                else:
                    print(f"No eligible MHWP found for patient '{patient}' with symptom '{symptom}'. Skipping.")

        #  Unassigned patients and all MHWPs with schedules already assigned
        elif unassigned_patients and mhwps_with_schedule.issubset(set(current_assignments.keys())):
            print("\n--- Assigning patients to MHWPs who already have assignments ---")
            for patient in list(unassigned_patients):
                symptom = patients_with_symptoms.get(patient)
                if not symptom:
                    print(f"No symptom found for patient '{patient}'. Skipping.")
                    continue

                eligible_mhwps = [
                    mhwp for mhwp in mhwps_with_major
                    if symptom in MATCHING_RULES.get(mhwps_with_major.get(mhwp, ""), set())
                ]

                if eligible_mhwps:
                    mhwp_with_least_patients = min(
                        eligible_mhwps,
                        key=lambda mhwp: len(current_assignments.get(mhwp, []))
                    )
                    current_assignments.setdefault(mhwp_with_least_patients, []).append(patient)
                    unassigned_patients.remove(patient)
                    print(f"Assigned: Patient '{patient}' -> MHWP '{mhwp_with_least_patients}'")
                else:
                    print(f"No eligible MHWP found for patient '{patient}' with symptom '{symptom}'. Skipping.")

        # Save the results and update related files
        save_assignments(current_assignments, assignments_path)
        update_mhwp_csv_with_assignments(assignments_path=assignments_path, mhwp_data_path=mhwp_data_path)
        update_patients_csv_with_assignments(assignments_path=assignments_path, patient_data_path=patient_data_path)

        print("\n--- Assignments Updated ---")



    else:
        print("\nInvalid choice. Returning to menu.")
        return


def display_unassigned_users(patient_data_path="data/patients.csv",
                             mhwp_data_path="data/mhwp.csv",
                             assignments_path="data/assignments.csv"):
    """
    Display unassigned patients and MHWPs in a table format.
    """
    all_patients = set(get_patients(patient_data_path))
    all_mhwps = set(get_mhwps(mhwp_data_path))

    current_assignments = get_current_assignments(assignments_path)
    assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
    assigned_mhwps = set(current_assignments.keys())

    unassigned_patients = all_patients - assigned_patients
    unassigned_mhwps = all_mhwps - assigned_mhwps

    table_data = [{"Name": user, "Role": "Patient", "Status": "Unassigned"} for user in unassigned_patients]
    table_data.extend({"Name": user, "Role": "MHWP", "Status": "Unassigned"} for user in unassigned_mhwps)

    if table_data:
        print("\nUnassigned Patients and MHWPs:")
        print(tabulate(table_data, headers="keys", tablefmt="grid"))
    else:
        print("\nAll patients and MHWPs are assigned.")



def display_assignments(assignments_path="data/assignments.csv", user_data_path="data/user_data.csv"):
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

def handle_admin_menu(user):
    """
    Admin menu to manage assignments, view unassigned users, and modify user data.
    """
    while True:
        print("\nAdmin Options:")
        print("1. Update Another User's Info")
        print("2. Delete Another User")
        print("3. View System Statistics")
        print("4. View All Assignments")
        print("5. Assign Patients to MHWPs")
        print("6. Modify Assignments")
        print("7. Initialize Assignments")  # Reset assignments
        print("8. Display Unassigned Patients and MHWPs")
        print("9. Initialize User Data")
        print("10. Logout")
        print("11. Initialize MHWP Schedule Data")

        admin_choice = input("Select an option (1-9): ").strip()

        if admin_choice == '1':  # Update another user's info
            target_username = input("Enter the username to update: ").strip()
            new_username = input("Enter the new username (blank to keep): ").strip()
            new_password = input("Enter the new password (blank to keep): ").strip()
            new_email = input("Enter the new email (blank to keep): ").strip()
            new_emergency_email = input("Enter the new emergency email (blank to keep): ").strip()

            user.admin_update_user(
                target_username,
                new_username or None,
                new_password or None,
                new_email or None,
                new_emergency_email or None
            )

        elif admin_choice == '2':  # Delete another user
            target_username = input("Enter the username to delete: ").strip()
            user.admin_delete_user(target_username)

        elif admin_choice == '3':  # View system statistics
            print("\nSystem statistics feature coming soon...")

        elif admin_choice == '4':  # View all assignments
            print("\n--- All Assignments ---")
            display_assignments("data/assignments.csv", "data/user_data.csv")

        elif admin_choice == '5':  # Assign patients to MHWPs
            print("\n--- Assigning Patients to MHWPs ---")
            balanced_assign_patients_and_mhwps(
                patient_data_path="data/patients.csv",
                mhwp_data_path="data/mhwp.csv",
                assignments_path="data/assignments.csv",
                schedule_path="data/mhwp_schedule.csv"
            )
            print("\n--- Updated Assignments ---")
            display_assignments("data/assignments.csv", "data/user_data.csv")

        elif admin_choice == '6':  # Modify Assignments
            print("\n--- Modify Assignments ---")
            modify_assignments(
              assignments_path="data/assignments.csv",
              patient_data_path="data/patients.csv",
              mhwp_data_path="data/mhwp.csv",
              schedule_path="data/mhwp_schedule.csv"
            )

        elif admin_choice == '7':  # Initialize Assignments
            print("\n--- Initializing Assignments ---")
            initialize_assignments("data/assignments.csv")
            print("Assignments have been reset.")

        elif admin_choice == '8':  # Display unassigned users
            print("\n--- Unassigned Patients and MHWPs ---")
            display_unassigned_users(
                patient_data_path="data/patients.csv",
                mhwp_data_path="data/mhwp.csv",
                assignments_path="data/assignments.csv"
            )
        elif admin_choice == '9':  # Initialize User Data
            print("\n--- Initializing User Data ---")
            initialize_user_data("data/user_data.csv")
            print("User data has been reset.")

        elif admin_choice == '10':  # Logout
            print("Logging out of admin session.")
            break


        elif admin_choice == '11':  # Initialize/clean MHWP Schedule Data

            print("\n--- Initializing MHWP Schedule Data ---")
            confirmation = input("This will clear all existing MHWP schedule data. Are you sure? (yes/no): ").strip().lower()
            
            if confirmation == 'yes':
                initialize_mhwp_schedule("data/mhwp_schedule.csv")
                print("MHWP schedule data has been reset.")
            else:
                print("Operation cancelled. MHWP schedule data remains unchanged.")

        else:
            print("Invalid choice, please try again.")
