
import pandas as pd
import os

# read csv files
def read_csv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Error: File '{file_path}' is empty.")
    except pd.errors.ParserError:
        raise ValueError(f"Error: File '{file_path}' contains invalid data.")

# load data from patients
def load_patient_data():
    try:
        return read_csv("patients.csv")
    except Exception as e:
        print(e)
        return pd.DataFrame()  # the empty DataFrame use to make sure the following stage

# load data from mood
def load_mood_data():
    try:
        return read_csv("moods.csv")
    except Exception as e:
        print(e)
        return pd.DataFrame()


def get_patients_by_mhwp(mhwp_username):
    patients = load_patient_data()
    if patients.empty:
        print("No patient data available.")
        return pd.DataFrame()
    return patients[patients["mhwp_username"] == mhwp_username]

# more information about patients
def get_patient_mood_data(patient_id):
    moods = load_mood_data()
    if moods.empty:
        print("No mood data available.")
        return pd.DataFrame()
    return moods[moods["patient_id"] == patient_id]

def generate_summary(mhwp_username):
    try:
        patients = get_patients_by_mhwp(mhwp_username)
        moods = load_mood_data()

        if patients.empty:
            print("No patient data available for summary.")
            return pd.DataFrame()

        summary = []
        for _, patient in patients.iterrows():
            patient_id = patient["patient_id"]
            mood_data = moods[moods["patient_id"] == patient_id]
            total_moods = len(mood_data)
            last_mood = (
                mood_data["mood_score"].iloc[-1] if not mood_data.empty else "N/A"
            )
            summary.append({
                "ID": patient_id,
                "Name": patient["name"],
                "Appointments": patient["total_appointments"],
                "Mood Entries": total_moods,
                "Last Mood": last_mood,
            })

        return pd.DataFrame(summary)

    except KeyError as e:
        print(f"Data error: Missing column {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error during summary generation: {e}")
        return pd.DataFrame()

import matplotlib.pyplot as plt

def plot_mood_tracking(patient_id, patient_name):
    try:
        mood_data = get_patient_mood_data(patient_id)
        if mood_data.empty:
            print(f"No mood data available for {patient_name}.")
            return

        # Make sure the date field exists and is formatted correctly
        if "date" not in mood_data.columns or "mood_score" not in mood_data.columns:
            print(f"Invalid data for patient {patient_name}. Skipping plot.")
            return

        # Check and process the date format
        try:
            mood_data["date"] = pd.to_datetime(mood_data["date"])
        except Exception:
            print(f"Error parsing dates for patient {patient_name}. Skipping plot.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(
            mood_data["date"], mood_data["mood_score"],
            marker="o", label="Mood Score"
        )
        plt.title(f"Mood Tracking for {patient_name}")
        plt.xlabel("Date")
        plt.ylabel("Mood Score")
        plt.grid()
        plt.legend()
        plt.show()

    except Exception as e:
        print(f"Error generating chart for patient {patient_name}: {e}")


def display_dashboard(mhwp_username):
    try:
        print("\nPatient Summary:")
        print("-------------------------------------------------")
        summary = generate_summary(mhwp_username)
        if summary.empty:
            print("No summary data available.")
            return
        print(summary.to_string(index=False))
        print("-------------------------------------------------")

        patients = get_patients_by_mhwp(mhwp_username)
        if patients.empty:
            print("No patients available for chart generation.")
            return

        for _, patient in patients.iterrows():
            print(f"\nGenerating mood chart for {patient['name']}...")
            plot_mood_tracking(patient["patient_id"], patient["name"])

    except Exception as e:
        print(f"Error displaying dashboard: {e}")


def table_of_patient():
    pass


def display_patient_summary(summary_data):
    """
    Display patient summary as a text table.
    :param summary_data: pandas.DataFrame containing patient summary information.
    """
    if summary_data.empty:
        print("No patient data available.")
        return

    print("Patient Summary:")
    print("-" * 60)
    print(summary_data.to_string(index=False))
    print("-" * 60)


def dashboard_menu(patient_username):
    """
    show menu of dashboard。
    """
    while True:
        print(f"\nPatient: {patient_username}")
        print("1. waiting")
        print("2. waiting")
        print("3. waiting")
        print("4. waiting")
        print("5. waiting")

        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            print('waiting')
        elif choice == "2":
            print('waiting')
        elif choice == "3":
            print('waiting')
        elif choice == "4":
            print('waiting')
        elif choice == "5":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice, please try again.")