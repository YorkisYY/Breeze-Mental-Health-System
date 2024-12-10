import pandas as pd
from services.comment import view_comments
from datetime import datetime

APPOINTMENTS_FILE = "data/appointments.csv"
MOOD_DATA_FILE = "data/mood_data.csv"
JOURNAL_ENTRIES_FILE = "data/patient_journaling.csv"
MENTAL_ASSESSMENTS_FILE = "data/mental_assessments.csv"
PATIENT_NOTES_FILE = "data/patient_notes.csv"


CONDITIONS = ["Anxiety", "Depression", "Autism", "Stress"]

def view_patient_records(mhwp_username):
    """
    Entry point for MHWP to view patient records.
    """
    try:
        # Get patients under MHWP
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)

        # Check if required columns are present
        if "mhwp_username" not in appointments_df.columns or "patient_username" not in appointments_df.columns:
            print("Error: CSV file is missing required columns.")
            return

        # Filter patients under MHWP
        patients = appointments_df[appointments_df["mhwp_username"] == mhwp_username]["patient_username"].unique()

        if not patients:
            print("You currently have no registered patients.")
            return

        print("\nYour Patients:")
        for idx, patient in enumerate(patients, start=1):
            print(f"{idx}. {patient}")

        patient_choice = input("Select a patient by number: ").strip()
        try:
            patient_username = patients[int(patient_choice) - 1]
        except (IndexError, ValueError):
            print("Invalid selection.")
            return

        # Navigate to patient record menu
        patient_record_menu(patient_username, mhwp_username)

    except FileNotFoundError:
        print(f"File not found: {APPOINTMENTS_FILE}")
    except Exception as e:
        print(f"Error viewing patient records: {e}")


def patient_record_menu(patient_username, mhwp_username):
    """
    Display options menu for patient records.
    """
    while True:
        print(f"\nPatient: {patient_username}")
        print("1. View Mood Tracker")
        print("2. View Patient Journaling")
        print("3. View Mental Health Assessments")
        print("4. View Patient Comment")
        print("5. Add Record to Patient")
        print("6. View Patient Medical Records")
        print("7. Return to Main Menu")

        choice = input("Select an option (1-7): ").strip()
        if choice == "1":
            view_mood_tracker(patient_username)
        elif choice == "2":
            view_patient_journaling(patient_username)
        elif choice == "3":
            view_mental_health_assessments(patient_username)
        elif choice == "4":
            view_comments(mhwp_username)
        elif choice == "5":
            add_record(patient_username)
        elif choice == "6":
            view_notes(mhwp_username)
        elif choice == "7":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice, please try again.")


def view_mood_tracker(patient_username):
    """
    View the patient's mood tracker data.
    """
    print("\n1. Mood Tracker:")
    try:
        mood_df = pd.read_csv(MOOD_DATA_FILE)
        patient_moods = mood_df[mood_df["username"] == patient_username]
        if not patient_moods.empty:
            print(patient_moods[["color_code", "comments", "timestamp"]].to_string(index=False))
        else:
            print("No mood tracker data available.")
    except FileNotFoundError:
        print("Mood Tracker file not found.")


def view_patient_journaling(patient_username):
    """
    View the patient's journaling data.
    """
    print("\n2. Patient Journaling:")
    try:
        journal_df = pd.read_csv(JOURNAL_ENTRIES_FILE)
        patient_journal = journal_df[journal_df["patient_username"] == patient_username]
        if not patient_journal.empty:
            print(patient_journal[["entry", "timestamp"]].to_string(index=False))
        else:
            print("No journaling available.")
    except FileNotFoundError:
        print("Journaling file not found.")


def view_mental_health_assessments(patient_username):
    """
    View the patient's mental health assessment scores and results.
    """
    print("\n3. Mental Health Assessments:")
    try:
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_FILE)
        patient_assessments = assessments_df[assessments_df["patient_username"] == patient_username]
        if not patient_assessments.empty:
            print(patient_assessments[["date", "score", "status"]].to_string(index=False))
        else:
            print("No mental health assessments available.")
    except FileNotFoundError:
        print("Mental Assessments file not found.")


def get_available_appointments(patient_username):
    """
    Get all eligible appointments for the patient.
    Conditions: status is 'confirmed' and time has passed.
    """
    try:
        # Read appointment data
        appointments = pd.read_csv(APPOINTMENTS_FILE)

        # Filter appointments belonging to the patient and create a copy
        patient_appointments = appointments[appointments["patient_username"] == patient_username].copy()

        if patient_appointments.empty:
            print("No appointments found for this patient.")
            return pd.DataFrame(), {}

        # Filter eligible appointments
        now = datetime.now()
        patient_appointments["datetime"] = pd.to_datetime(
            patient_appointments["date"] + " " + patient_appointments["timeslot"].str.split("-").str[0]
        )
        available_appointments = patient_appointments[
            (patient_appointments["status"] == "confirmed") & (patient_appointments["datetime"] < now)
        ].reset_index(drop=True)

        if available_appointments.empty:
            print("No appointments available for action.")
            return pd.DataFrame(), {}

        # Display available appointments
        print("\nAvailable appointments:")
        print("--------------------------------------------------------------")
        print("Option | Appointment ID | Date       | Time      | MHWP Username")
        print("--------------------------------------------------------------")
        option_map = {}  # Map option to DataFrame index
        for idx, (i, row) in enumerate(available_appointments.iterrows(), start=1):  # Start numbering from 1
            print(f"{idx:<6} | {row['id']:<14} | {row['date']} | {row['timeslot']} | {row['mhwp_username']}")
            option_map[idx] = i  # Save the mapping between option and DataFrame index
        print("--------------------------------------------------------------")

        return available_appointments, option_map
    except Exception as e:
        print(f"Error loading appointments: {e}")
        return pd.DataFrame(), {}


def add_record(patient_username):
    """
    Add a medical record based on the logged-in user's username and appointment information.
    """
    available_appointments, option_map = get_available_appointments(patient_username)

    if not available_appointments.empty:
        try:
            # User inputs option
            option = int(input("Select an appointment option to add a record (1, 2, ...): "))

            # Check if the option is valid
            if option not in option_map:
                print("Invalid option selected.")
                return

            # Use the option to find the corresponding DataFrame row
            selected_appointment = available_appointments.iloc[option_map[option]]
            appointment_id = int(selected_appointment["id"])
            mhwp_username = selected_appointment["mhwp_username"]
            appointment_date = pd.to_datetime(selected_appointment["date"], format="%Y/%m/%d").strftime("%Y-%m-%d")

            # Check if a record already exists
            try:
                notes_df = pd.read_csv(PATIENT_NOTES_FILE)
                if not notes_df.empty and appointment_id in notes_df["id"].values:
                    print("A record already exists for this appointment.")
                    return
            except FileNotFoundError:
                notes_df = pd.DataFrame()  # Initialize empty DataFrame if the file doesn't exist

            print("Select a mental condition to record:")
            for idx, condition in enumerate(CONDITIONS, start=1):
                print(f"{idx}. {condition}")

            condition_choice = input("Select a condition by number: ").strip()
            try:
                condition = CONDITIONS[int(condition_choice) - 1]
            except (IndexError, ValueError):
                print("Invalid selection.")
                return

            # Enter notes manually
            notes = input("Enter notes or additional details (optional): ").strip()

            # Add record
            record_data = {
                "patient_username": patient_username,
                "mhwp_username": mhwp_username,
                "date": appointment_date,
                "condition": condition,
                "notes": notes,
                "id": appointment_id,
            }
            notes_df = pd.concat([notes_df, pd.DataFrame([record_data])], ignore_index=True)

            # Save the record
            notes_df.to_csv(PATIENT_NOTES_FILE, index=False)
            print("Record added successfully!")

        except ValueError:
            print("Invalid input. Please select a valid option.")
        except Exception as e:
            print(f"Error adding record: {e}")


def view_notes(mhwp_username):
    """
    View all medical records for a specific MHWP.
    """
    try:
        # Load medical records file
        notes_df = pd.read_csv(PATIENT_NOTES_FILE)

        # Filter records belonging to the MHWP
        mhwp_notes = notes_df[notes_df["mhwp_username"] == mhwp_username]

        if mhwp_notes.empty:
            print(f"No records found for MHWP '{mhwp_username}'.")
        else:
            print(f"\nRecords for MHWP '{mhwp_username}':")
            print("------------------------------------------------------------------")
            print("Patient      | Date       | Condition          | Notes")
            print("------------------------------------------------------------------")
            for _, row in mhwp_notes.iterrows():
                print(f"{row['patient_username']:<12} | {row['date']} | {row['condition']:<18} | {row['notes']}")
            print("------------------------------------------------------------------")

    except FileNotFoundError:
        print("No records file found. Please initialize it first.")
    except Exception as e:
        print(f"Error viewing records: {e}")


def view_my_records(patient_username):
    """
    Allow a patient to view their medical records, including date, condition, and notes, in a paginated format.
    """
    try:
        # Load patient notes file
        notes_df = pd.read_csv(PATIENT_NOTES_FILE)
    except FileNotFoundError:
        # If file does not exist, create an empty DataFrame and save it
        notes_df = pd.DataFrame(columns=["patient_username", "mhwp_username", "date", "condition", "notes", "id"])
        notes_df.to_csv(PATIENT_NOTES_FILE, index=False)
        print("No medical records found. File has been initialized.")
        return

    # Filter records for the current patient
    patient_records = notes_df[notes_df["patient_username"] == patient_username]

    if patient_records.empty:
        print("No medical records found for you.")
        return

    # Select relevant columns and sort by date (latest first)
    filtered_records = patient_records[["date", "condition", "notes"]].sort_values(by="date", ascending=False)

    # Pagination logic
    records_per_page = 5
    total_records = len(filtered_records)
    total_pages = (total_records + records_per_page - 1) // records_per_page  # Round up division
    current_page = 1

    while True:
        # Display current page records
        start_idx = (current_page - 1) * records_per_page
        end_idx = start_idx + records_per_page
        page_records = filtered_records.iloc[start_idx:end_idx]

        print(f"\nPage {current_page}/{total_pages}")
        print(page_records.to_string(index=False))  # Display without the DataFrame index

        # Pagination navigation
        if total_pages > 1:
            print("\nOptions:")
            if current_page > 1:
                print("1. Previous Page")
            if current_page < total_pages:
                print("2. Next Page")
            print("3. Quit Viewing")

            choice = input("Select an option: ").strip().lower()
            if choice == "1" and current_page > 1:
                current_page -= 1
            elif choice == "2" and current_page < total_pages:
                current_page += 1
            elif choice == "3":
                print("Exiting medical records view.")
                break
            else:
                print("Invalid choice, please try again.")
        else:
            print("\nNo more pages to navigate.")
            break
        
        
        


