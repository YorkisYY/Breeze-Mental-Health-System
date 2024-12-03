import pandas as pd
from services.comment import view_comments
from datetime import datetime

APPOINTMENTS_FILE = "data/appointments.csv"
MOOD_DATA_FILE = "data/mood_data.csv"
JOURNAL_ENTRIES_FILE = "data/patient_journaling.csv"
MENTAL_ASSESSMENTS_FILE = "data/mental_assessments.csv"
PATIENT_NOTES_FILE="data/patient_notes.csv"


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
        patient_record_menu(patient_username, mhwp_username)

    except FileNotFoundError:
        print(f"File not found: {APPOINTMENTS_FILE}")
    except Exception as e:
        print(f"Error viewing patient records: {e}")



def patient_record_menu(patient_username, mhwp_username):
    """
    展示患者记录选项菜单。
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

        choice = input("Select an option (1-5): ").strip()
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


def get_available_appointments(patient_username):
    """
    获取患者所有符合条件的预约列表。
    条件：status 为 confirmed 且时间已过去。
    """
    try:
        # 读取预约数据
        appointments = pd.read_csv(APPOINTMENTS_FILE)

        # 筛选属于该患者的预约，并创建副本
        patient_appointments = appointments[appointments["patient_username"] == patient_username].copy()

        if patient_appointments.empty:
            print("No appointments found for this patient.")
            return pd.DataFrame(), {}

        # 筛选符合条件的预约
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

        # 显示可选预约
        print("\nAvailable appointments:")
        print("--------------------------------------------------------------")
        print("Option | Appointment ID | Date       | Time      | MHWP Username")
        print("--------------------------------------------------------------")
        option_map = {}  # 映射 Option 和 DataFrame 索引
        for idx, (i, row) in enumerate(available_appointments.iterrows(), start=1):  # 从 1 开始编号
            print(f"{idx:<6} | {row['id']:<14} | {row['date']} | {row['timeslot']} | {row['mhwp_username']}")
            option_map[idx] = i  # 保存 Option 和 DataFrame 索引的映射
        print("--------------------------------------------------------------")
        

        return available_appointments, option_map
    except Exception as e:
        print(f"Error loading appointments: {e}")
        return pd.DataFrame(), {}


def add_record(patient_username):
    """
    添加病例记录，基于登录用户的用户名获取预约信息。
    """
    available_appointments, option_map = get_available_appointments(patient_username)

    if not available_appointments.empty:
        try:
            # 用户输入 Option
            option = int(input("Select an appointment option to add a record (1, 2, ...): "))

            # 检查 Option 是否有效
            if option not in option_map:
                print("Invalid option selected.")
                return

            # 使用 Option 找到对应的 DataFrame 行
            selected_appointment = available_appointments.iloc[option_map[option]]
            appointment_id = int(selected_appointment["id"])
            mhwp_username = selected_appointment["mhwp_username"]
            appointment_date = selected_appointment["date"]

            appointment_date = pd.to_datetime(selected_appointment["date"], format="%Y/%m/%d").strftime("%Y-%m-%d")

            # 检查是否已添加记录
            try:
                notes_df = pd.read_csv(PATIENT_NOTES_FILE)
                if not notes_df.empty and appointment_id in notes_df["id"].values:
                    print("A record already exists for this appointment.")
                    return
            except FileNotFoundError:
                notes_df = pd.DataFrame()  # 文件不存在时，初始化空 DataFrame

            
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

            # 添加记录
            record_data = {
                "patient_username": patient_username,
                "mhwp_username": mhwp_username,
                "date": appointment_date,
                "condition": condition,
                "notes": notes,
                "id": appointment_id,
            }
            notes_df = pd.concat([notes_df, pd.DataFrame([record_data])], ignore_index=True)

            
            # 保存记录
            notes_df.to_csv(PATIENT_NOTES_FILE, index=False)
            print("Record added successfully!")

        except ValueError:
            print("Invalid input. Please select a valid option.")
        except Exception as e:
            print(f"Error adding record: {e}")


def view_notes(mhwp_username):
    """
    查看某 MHWP 的所有病例记录。
    """
    try:
        # 加载病例记录文件
        notes_df = pd.read_csv(PATIENT_NOTES_FILE)

        # 筛选出属于该 MHWP 的病例记录
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
        
        
        
        


