import pandas as pd

APPOINTMENTS_FILE = "data/appointments.csv"
MOOD_DATA_FILE = "data/mood_data.csv"
JOURNAL_ENTRIES_FILE = "data/journal_entries.csv"
MENTAL_ASSESSMENTS_FILE = "data/mental_assessments.csv"

CONDITIONS = ["Anxiety", "Depression", "Autism", "Stress"]

def view_patient_records(mhwp_username):
    """
    MHWP 查看患者记录功能入口。
    """
    try:
        # 获取 MHWP 名下的患者
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)
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

        # 跳转到患者记录菜单
        patient_record_menu(patient_username)

    except Exception as e:
        print(f"Error viewing patient records: {e}")


def patient_record_menu(patient_username):
    """
    展示患者记录选项菜单。
    """
    while True:
        print(f"\nPatient: {patient_username}")
        print("1. View Mood Tracker")
        print("2. View Journaling Entries")
        print("3. View Mental Health Assessments")
        print("4. Add Record to Patient")
        print("5. Return to Main Menu")

        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            view_mood_tracker(patient_username)
        elif choice == "2":
            view_journaling_entries(patient_username)
        elif choice == "3":
            view_mental_health_assessments(patient_username)
        elif choice == "4":
            add_patient_record(patient_username)
        elif choice == "5":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice, please try again.")


def view_mood_tracker(patient_username):
    """
    查看患者的 Mood Tracker 数据。
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


def view_journaling_entries(patient_username):
    """
    查看患者的 Journaling 数据。
    """
    print("\n2. Journaling Entries:")
    try:
        journal_df = pd.read_csv(JOURNAL_ENTRIES_FILE)
        patient_journal = journal_df[journal_df["username"] == patient_username]
        if not patient_journal.empty:
            print(patient_journal[["entry", "timestamp"]].to_string(index=False))
        else:
            print("No journaling entries available.")
    except FileNotFoundError:
        print("Journal Entries file not found.")


def view_mental_health_assessments(patient_username):
    """
    查看患者的心理问卷分数及结果。
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


def add_patient_record(patient_username):
    """
    为患者添加心理状态记录和备注。
    """
    print("\n4. Add Patient Record:")
    print("Select a mental condition to record:")
    for idx, condition in enumerate(CONDITIONS, start=1):
        print(f"{idx}. {condition}")
    
    condition_choice = input("Select a condition by number: ").strip()
    try:
        condition = CONDITIONS[int(condition_choice) - 1]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return

    notes = input("Enter notes or additional details (optional): ").strip()

    # 保存记录到 mental_assessments.csv
    new_record = {
        "patient_username": patient_username,
        "mhwp_username": None,  # 在此场景中不需要指定 MHWP
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "score": None,  # 不涉及分数
        "status": condition
    }
    try:
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_FILE)
        assessments_df = assessments_df.append(new_record, ignore_index=True)
    except FileNotFoundError:
        assessments_df = pd.DataFrame([new_record])

    assessments_df.to_csv(MENTAL_ASSESSMENTS_FILE, index=False)
    print("Patient record added successfully!")
