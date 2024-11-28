import pandas as pd

APPOINTMENTS_FILE = "data/appointments.csv"
MOOD_DATA_FILE = "data/mood_data.csv"
JOURNAL_ENTRIES_FILE = "data/patient_journaling.csv"
MENTAL_ASSESSMENTS_FILE = "data/mental_assessments.csv"

CONDITIONS = ["Anxiety", "Depression", "Autism", "Stress"]

def view_patient_records(mhwp_username):
    """
    MHWP 查看患者记录功能入口。
    """
    try:
        # 获取 MHWP 名下的患者
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)

        # 检查是否包含预期的列
        if "mhwp_username" not in appointments_df.columns or "patient_username" not in appointments_df.columns:
            print("Error: CSV file is missing required columns.")
            return

        # 筛选 MHWP 名下的患者
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

    except FileNotFoundError:
        print(f"File not found: {APPOINTMENTS_FILE}")
    except Exception as e:
        print(f"Error viewing patient records: {e}")



def patient_record_menu(patient_username):
    """
    展示患者记录选项菜单。
    """
    while True:
        print(f"\nPatient: {patient_username}")
        print("1. View Mood Tracker")
        print("2. View Patient Journaling")
        print("3. View Mental Health Assessments")
        print("4. Add Record to Patient")
        print("5. Return to Main Menu")

        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            view_mood_tracker(patient_username)
        elif choice == "2":
            view_patient_journaling(patient_username)
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


def view_patient_journaling(patient_username):
    """
    查看患者的 Journaling 数据。
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
    为患者添加手动评价
    """
    try:
        # 从 appointments.csv 获取 mhwp_username
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)
        mhwp_record = appointments_df[appointments_df["patient_username"] == patient_username]
        if mhwp_record.empty:
            print("Error: No MHWP found for this patient.")
            return
        mhwp_username = mhwp_record.iloc[0]["mhwp_username"]  # 提取 mhwp_username
    except FileNotFoundError:
        print(f"Error: File {APPOINTMENTS_FILE} not found.")
        return

    print("\nAdd Patient Record:")

    # 手动输入 condition
    CONDITIONS = ["Anxiety", "Depression", "Autism", "Stress"]
    print("Select a mental condition to record:")
    for idx, condition in enumerate(CONDITIONS, start=1):
        print(f"{idx}. {condition}")

    condition_choice = input("Select a condition by number: ").strip()
    try:
        condition = CONDITIONS[int(condition_choice) - 1]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return

    # 手动输入 notes
    notes = input("Enter notes or additional details (optional): ").strip()

    # 生成新评价数据
    new_note = {
        "patient_username": patient_username,
        "mhwp_username": mhwp_username,
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "condition": condition,
        "notes": notes
    }

    # 保存记录到 patient_notes.csv
    try:
        notes_df = pd.read_csv("data/patient_notes.csv")
        notes_df = pd.concat([notes_df, pd.DataFrame([new_note])], ignore_index=True)
    except FileNotFoundError:
        notes_df = pd.DataFrame([new_note])

    notes_df.to_csv("data/patient_notes.csv", index=False)
    print("Patient note added successfully!")


