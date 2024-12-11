from .admin_assignment import *
from config import *

def get_patients(patient_data_path=PATIENTS_DATA_PATH):
    """Get patient usernames from patients.csv"""
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

def get_mhwps(mhwp_data_path=MHWP_DATA_PATH):
    """Get MHWP usernames from mhwp.csv"""
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

def display_unassigned_users(
    patient_data_path=PATIENTS_DATA_PATH,
    mhwp_data_path=MHWP_DATA_PATH,
    assignments_path=ASSIGNMENTS_DATA_PATH
):
    """Display unassigned users"""
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

def balanced_assign_patients_and_mhwps(
    patient_data_path=PATIENTS_DATA_PATH,
    mhwp_data_path=MHWP_DATA_PATH,
    assignments_path=ASSIGNMENTS_DATA_PATH,
    schedule_path=SCHEDULE_DATA_PATH
):
    """Assign patients to MHWPs"""

    # Load necessary data
    eligible_mhwps = get_mhwps_with_schedule(schedule_path)  # get schedule with MHWPs
    patients_with_symptoms = get_patients_with_symptoms(patient_data_path)
    mhwps_with_major = get_mhwps_with_major(mhwp_data_path)
    current_assignments = get_current_assignments(assignments_path)

    if not eligible_mhwps:
        print("Can't complete assignments due to all MHWPs don't set schedules.")
        return

    all_mhwps = set(mhwps_with_major.keys())
    mhwps_without_schedule = all_mhwps - eligible_mhwps

    if mhwps_without_schedule:
        for mhwp in mhwps_without_schedule:
            print(f" MHWP '{mhwp}' can't be assigned due to no schedule.")

    assignments = {mhwp: patients.copy() for mhwp, patients in current_assignments.items()}

    # Get currently assigned patients
    already_assigned_patients = {patient for patients in current_assignments.values() for patient in patients}

    # Filter out already assigned patients
    unassigned_patients = {patient: symptom 
                          for patient, symptom in patients_with_symptoms.items() 
                          if patient not in already_assigned_patients}

    assigned_mhwp_tracker = {mhwp: False for mhwp in eligible_mhwps}

    # assign to unassigned patients only
    for patient, symptom in unassigned_patients.items():
        # obtain mhwps who set schedules (according matching rules)
        eligible_mhwps_for_patient = [
            mhwp for mhwp, major in mhwps_with_major.items()
            if mhwp in eligible_mhwps and symptom in MATCHING_RULES.get(major, set())
        ]

        if eligible_mhwps_for_patient:
            unassigned_mhwps = [mhwp for mhwp in eligible_mhwps_for_patient if not assigned_mhwp_tracker[mhwp]]

            if unassigned_mhwps:
                # priority to assign unassigned mhwp
                selected_mhwp = random.choice(unassigned_mhwps)
                assigned_mhwp_tracker[selected_mhwp] = True
            else:
                selected_mhwp = random.choice(eligible_mhwps_for_patient)

            assignments.setdefault(selected_mhwp, []).append(patient)
            print(f"Patient '{patient}' -> MHWP '{selected_mhwp}' (Major: {mhwps_with_major[selected_mhwp]})")
        else:
            print(f"Patient '{patient}'  can't be assigned due to no eligible MHWP.")

    # save assignments
    save_assignments(assignments, assignments_path)
    # unpdate files
    update_mhwp_csv_with_assignments(assignments_path=assignments_path, mhwp_data_path=mhwp_data_path)
    update_patients_csv_with_assignments(assignments_path=assignments_path, patient_data_path=patient_data_path)
    assignments_completed = True
    print("Assignments completed successfully.")