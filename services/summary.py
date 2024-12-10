import pandas as pd
import os
from tabulate import tabulate
from datetime import datetime, timedelta
from config import ASSIGNMENTS_DATA_PATH, APPOINTMENTS_DATA_PATH

# read csv files
def read_csv(file_path):
    """
    Reads CSV and handles specific errors.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError: # In case the file is totally empty
        raise ValueError(f"Error: File '{file_path}' is empty.")
    except pd.errors.ParserError: # In case the format of file is wrong
        raise ValueError(f"Error: File '{file_path}' contains invalid data.")
    except Exception as e:
        raise ValueError(f"Error loading file '{file_path}': {e}")


# load data from assignments
def load_assignments():
    try:
        return read_csv(ASSIGNMENTS_DATA_PATH)
    except Exception as e:
        print(e)
        return pd.DataFrame() # Returning empty DataFrame in case of an error(make sure the safe of following stage)

# load data from appointments
def load_appointments():
    try:
        return read_csv(APPOINTMENTS_DATA_PATH)
    except Exception as e:
        print(e)
        return pd.DataFrame() # Returning empty DataFrame in case of an error(make sure the safe of following stage)

def thisWeek():
    # 获取当前日期范围
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    week_end = week_start + timedelta(days=6)  # 本周日
    return week_start, week_end

# 获取预约
def get_bookings(appointments, start_date, end_date, status):


    # 转换日期格式
    appointments["date"] = pd.to_datetime(appointments["date"], format="%Y/%m/%d")

    # print(appointments)

    if status == "all":
        # 如果选择了 "all"，就筛选出指定时间范围内的所有预约
        filtered_appointments = appointments[
        (appointments["date"] >= start_date) &
        (appointments["date"] <= end_date)
        ]
        status_counts = filtered_appointments['status'].value_counts()

    elif status == "Separate statistics":
        # 如果选择了 "Separate statistics"，按 MHWP 和状态分组，统计每个 MHWP 各状态的数量
        filtered_appointments = appointments[
            (appointments["date"] >= start_date) &
            (appointments["date"] <= end_date)
            ]
        # 根据 'mhwp_username' 和 'status' 分组，统计每个 MHWP 对应的每个状态的预约数量
        status_counts = filtered_appointments.groupby(['mhwp_username', 'status']).size().unstack(fill_value=0)

    else:
    # 筛选确认状态的预约且日期在本周范围内
        filtered_appointments = appointments[
            (appointments["status"] == status) &
            (appointments["date"] >= start_date) &
            (appointments["date"] <= end_date)
            ]

    # 统计每个 MHWP 的状态预约数量
        status_counts = filtered_appointments["mhwp_username"].value_counts()
    return status_counts

# appointments = load_appointments()
# start_date = datetime.strptime("2024/10/01", "%Y/%m/%d")
# end_date = datetime.strptime("2024/12/30", "%Y/%m/%d")
#
# results = get_bookings(appointments, start_date, end_date, "Separate statistics")
# print(results)

# # 汇总分配和预约详情
# def generate_summary():
#     # 加载数据
#     assignments = load_assignments()
#     appointments = load_appointments()
#
#     # 汇总患者与 MHWPs 的分配
#     assignment_summary = assignments.groupby("mhwp_username")["patient_username"].apply(list)
#
#     # 统计当前一周的确认预约数量
#     confirmed_counts = get_confirmed_bookings_this_week(appointments)
#
#     # 创建结果表
#     summary = pd.DataFrame({
#         "MHWP": assignment_summary.index,
#         "Patients": assignment_summary.values,
#         "Confirmed Bookings (This Week)": [confirmed_counts.get(mhwp, 0) for mhwp in assignment_summary.index]
#     })
#
#     return summary


# 展示结果
# def display_summary():
#     try:
#         summary = generate_summary()
#         print("Summary of Assignments and Bookings:")
#         print(summary.to_string(index=False))
#     except Exception as e:
#         print(f"Error generating summary: {e}")
#


#
# def plot_appointment_trends(appointments):
#     # 按日期统计预约数量
#     appointment_counts = appointments.groupby('date').size()
#
#     # 生成折线图显示预约数量趋势
#     plt.figure(figsize=(10, 6))
#     plt.plot(appointment_counts.index, appointment_counts.values, marker='o')
#     plt.title('Appointments Trend')
#     plt.xlabel('Date')
#     plt.ylabel('Number of Appointments')
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.show()
# #
# def get_patients_by_mhwp(mhwp_username):
#     patients = load_patient_data()
#     if patients.empty: # In case the file just have Table head without any data rows
#         print("No patient data available.")
#         return pd.DataFrame()
#     return patients[patients["assigned_mhwp"] == mhwp_username]

# more information about patients
# def get_patient_mood_data(username):
#     moods = load_mood_data()
#     if moods.empty: # In case the file just have Table head without any data rows
#         print("No mood data available.")
#         return pd.DataFrame()
#     return moods[moods["username"] == username]

color_code_to_score = {
    "Green": 1,
    "Blue": 2,
    "Yellow": 3,
    "Orange": 4,
    "Red": 5,
}
#
# def generate_summary(mhwp_username):
#     try:
#         patients = get_patients_by_mhwp(mhwp_username)
#         moods = load_mood_data()
#
#         if patients.empty:
#             print("No patient data available for summary.")
#             return pd.DataFrame()
#
#         summary = []
#         for _, patient in patients.iterrows():
#             username = patient["username"]
#             mood_data = moods[moods["username"] == username] # Mood of one patient
#
#             total_moods = len(mood_data)
#
#             if total_moods == 0:
#                 last_mood = "N/A"
#                 average_mood = "N/A"
#             else:
#                 mood_data = mood_data.sort_values(by="timestamp", ascending=False)
#
#
#                 last_mood = mood_data.iloc[0]["color_code"]
#                 mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)
#                 average_mood = mood_data["mood_score"].mean()
#
#
#             summary.append({
#                 "username": username,
#                 #"Name": patient["username"],
#                 #"Appointments": patient["total_appointments"],
#                 "Mood Entries": total_moods,
#                 "Last Mood": last_mood,
#                 "Average Mood Score": average_mood
#             })
#
#         return pd.DataFrame(summary)
#
#     except KeyError as e: # In case nonexistent columns
#         print(f"Data error: Missing column {e}")
#         return pd.DataFrame()
#     except Exception as e:
#         print(f"Unexpected error during summary generation: {e}")
#         return pd.DataFrame()
#
#



def display_patient_summary_tabulate(summary_data):
    """
    Display patient summary using tabulate for better formatting.
    :param summary_data: List of dictionaries containing patient summary.
    """
    if summary_data.empty:
        print("No patient data available.")
        return

    print("Patient Summary:")
    print(tabulate(summary_data, headers="keys", tablefmt="grid"))

#
# def display_patient_summary(summary_data):
#     """
#     Display patient summary as a text table.
#     :param summary_data: pandas.DataFrame containing patient summary information.
#     """
#     if summary_data.empty:
#         print("No patient data available.")
#         return
#
#     print("Patient Summary:")
#     print("-" * 60)
#     print(summary_data.to_string(index=False))
#     print("-" * 60)

#
# import matplotlib.pyplot as plt
#
# # color_code to color mapping for the pie chart
# color_mapping = {
#     "Green": "green",
#     "Blue": "blue",
#     "Yellow": "yellow",
#     "Orange": "orange",
#     "Red": "red"
# }
#
# def plot_mood(patient_username):
#     try:
#         moods = load_mood_data()
#
#         if moods.empty:
#             print("No mood data found.")
#             return
#
#         mood_data = moods[moods["username"] == patient_username]
#
#             # 如果没有情绪数据，跳过
#         if mood_data.empty:
#             print(f"No mood data available for patient {patient_username}.")
#             return
#             # 按时间排序情绪数据
#         mood_data = mood_data.sort_values(by="timestamp", ascending=True)
#
#             # 将颜色码映射为评分
#         mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)
#
#
#         try:    # 画出情绪评分的折线图
#             plt.figure(figsize=(10, 5))
#             plt.plot(mood_data["timestamp"], mood_data["mood_score"], label=f"{patient_username}'s Mood Trend",
#                     marker='o')
#             plt.xlabel("Timestamp")
#             plt.ylabel("Mood Score (1 = Green, 5 = Red)")
#             plt.title(f"Mood Trend for {patient_username}")
#             plt.xticks(rotation=45)
#             plt.legend()
#             plt.tight_layout()
#             plt.show()
#         except Exception as e:
#             print(f"Error while plotting mood trend: {e}")
#
#         try:
#             #显示情绪状态分布的饼图
#             mood_counts = mood_data["color_code"].value_counts()
#             # 使用颜色映射将每个情绪状态对应颜色
#             colors = [color_mapping.get(x) for x in mood_counts.index]
#             plt.figure(figsize=(7, 7))
#             mood_counts.plot(kind='pie', autopct='%1.1f%%',
#                              colors=colors,
#                              startangle=90, counterclock=False)  # startangle设置起始角度
#             plt.title("Mood Status Distribution")
#             plt.ylabel("")  # 去掉y轴标签
#             plt.show()
#         except Exception as e:
#             print(f"Error while generating mood pie chart: {e}")
#
#
#
#     except Exception as e:
#         print(f"Error while generating mood trend plots: {e}")
#


def display_summary():
    try:
        appointments = load_appointments()
        start_date, end_date = thisWeek()
        results = get_bookings(appointments, start_date, end_date, "confirmed")


        # print(results)

        if results.empty:
            print("No summary data available.")
        else:
            print("Appointments confirmed for the current week")
            print(results)

            #display_patient_summary_tabulate(results)

        while True:
            print(f"\nWhat do you want to do next?")
            print("1. Modify the time range and status of the summary")
            print("2. See specific MHWP details")
            print("3. Returning to main menu")

            choice = input("Select an option (1-3): ").strip()
            if choice == "1":
                appointments = load_appointments()
                start_date = input("Enter start date (YYYY/MM/DD): ")
                end_date = input("Enter end date (YYYY/MM/DD): ")
                start_date = datetime.strptime(start_date, "%Y/%m/%d")
                end_date = datetime.strptime(end_date, "%Y/%m/%d")
                if start_date > end_date:
                    print("Invalid data, please try again.")
                    continue
                status = input("Enter status(1-4), 1:cancelled, 2:confirmed, 3:pending, 4:all, 5:separate statistics):")
                if status == "1":
                    results = get_bookings(appointments, start_date, end_date, "cancelled")
                elif status == "2":
                    results = get_bookings(appointments, start_date, end_date, "confirmed")
                elif status == "3":
                    results = get_bookings(appointments, start_date, end_date, "pending")
                elif status == "4":
                    results = get_bookings(appointments, start_date, end_date, "all")
                elif status == "5":
                    results = get_bookings(appointments, start_date, end_date, "Separate statistics")

                else:
                    print("Invalid choice, please try again.")


                # print(get_bookings(appointments, start_date, end_date, "all"))
                # print(get_bookings(appointments, start_date, end_date, "Separate statistics"))
                #
                #
                #
                print(results)

                #医生预约病人分布图
                #医生预约数量变化图
                #医生预约状态分布图
                #

            elif choice == "2":
                pass
                print("do it or not?")
                # appointments = pd.read_csv('appointment.csv')
                # plot_appointment_trends(appointments)
                # print("Returning to main menu.")
                # break


            elif choice == "3":
                print("Returning to main menu.")
                break

            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"Error displaying summary: {e}")

if __name__ == '__main__':
    display_summary()
