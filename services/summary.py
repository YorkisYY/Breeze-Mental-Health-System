import pandas as pd
import os
from tabulate import tabulate
from datetime import datetime, timedelta
from config import ASSIGNMENTS_DATA_PATH, APPOINTMENTS_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH



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




def print_result(result):
    # 如果 result 是 Series, 转换成 DataFrame
    if isinstance(result, pd.Series):
        result_df = result.to_frame(name='count')
    else:
        result_df = result  # 如果已经是 DataFrame，则直接使用


    print()

    print(tabulate(result_df, headers='keys', tablefmt='grid', showindex=True))

def get_valid_date_input(prompt):
    while True:
        user_input = input(prompt).strip()
        try:
            # 尝试将输入转化为日期格式 (YYYY/MM/DD)
            date = datetime.strptime(user_input, "%Y/%m/%d")
            return date
        except ValueError:
            print("Invalid date format. Please use YYYY/MM/DD format.")


def display_booking_summary():
    try:
        appointments = load_appointments()
        start_date, end_date = thisWeek()
        results = get_bookings(appointments, start_date, end_date, "confirmed")

        if results.empty:
            print("No summary data available.")
        else:
            print("Appointments confirmed for the current week")

            print_result(results)

        while True:
            print(f"\nWhat do you want to do next?")
            print("1. Modify the time range and status of the summary")

            print("2. Returning to main menu")

            choice = input("Select an option (1-2): ").strip()
            if choice == "1":

                appointments = load_appointments()

                start_date = get_valid_date_input("Enter start date (YYYY/MM/DD): ")
                end_date = get_valid_date_input("Enter end date (YYYY/MM/DD): ")
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

                print_result(results)

            elif choice == "2":
                print("Returning to last menu.")
                break

            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"Error displaying booking summary: {e}")


def display_summary():
    try:
        while True:
            print(f"\nWhat do you want to do?")
            print("1. See the summary of booking")
            print("2. Displays information about MHWPs and their patients")
            print("3. Returning to main menu")
            type = input("Select an option (1-3): ").strip()
            if type == "1":
                display_booking_summary()
            elif type == "2":
                display_mhwp_summary()
                view_patients_for_mhwp()

            elif type == "3":
                print("Returning to main menu.")
                break

            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"Error displaying summary: {e}")


def load_patients():
    try:
        return read_csv(PATIENTS_DATA_PATH)
    except Exception as e:
        print(e)
        return pd.DataFrame()


def load_mhwp():
    try:
        return read_csv(MHWP_DATA_PATH)
    except Exception as e:
        print(e)
        return pd.DataFrame()  # 如果加载失败，返回空的DataFrame



def get_patients_for_mhwp(mhwp_name):
    # 加载患者数据和分配数据
    patients = load_patients()

    mhwp = load_mhwp()

    # 找到该MHWP负责的所有患者
    mhwp_info = mhwp[mhwp['username'] == mhwp_name]

    if mhwp_info.empty:
        print(f"No information found for MHWP {mhwp_name}.")
        return

    assigned_patients = mhwp_info['assigned_patients'].values[0]
    assigned_patients_list = assigned_patients.split(',') if assigned_patients else []

    if not assigned_patients_list:
        print(f"MHWP {mhwp_name} has no assigned patients.")
        return

    # 根据患者用户名获取患者的基本信息
    patients_assigned = patients[patients['username'].isin(assigned_patients_list)]

    #     重置索引并移除原始的索引列
    patients_assigned = patients_assigned.reset_index(drop=True)

    # 输出该MHWP负责的所有患者信息
    print(f"Patients assigned to MHWP {mhwp_name}:")
    # print(patients_assigned[['username', 'symptoms', 'registration_date']])
    print(tabulate(patients_assigned[['username', 'symptoms', 'registration_date']], headers='keys', tablefmt='grid',
                   showindex=False))

def calculate_mhwp_patient_counts():
    # 加载数据
    mhwp = load_mhwp()
    patients = load_patients()
    assignments = load_assignments()

    # 创建一个空的列表来存储MHWP和患者数
    mhwp_patient_counts = []

    # 遍历每个MHWP
    for _, mhwp_row in mhwp.iterrows():
        mhwp_name = mhwp_row['username']
        mhwp_major = mhwp_row['major']

        # 获取MHWP负责的患者列表
        assigned_patients = mhwp_row['assigned_patients']
        if pd.isna(assigned_patients):
            patient_count = 0
        else:
            assigned_patients_list = assigned_patients.split(',')
            patient_count = len(assigned_patients_list)

        # 将信息添加到列表
        mhwp_patient_counts.append([mhwp_name, mhwp_major, patient_count])

    # 转换为DataFrame
    mhwp_summary_df = pd.DataFrame(mhwp_patient_counts,
                                   columns=['MHWP Name', 'Specialization (Major)', 'Assigned Patient Count'])

    # 返回DataFrame
    return mhwp_summary_df


# 展示MHWP及其患者数和专业领域
def display_mhwp_summary():
    mhwp_summary_df = calculate_mhwp_patient_counts()

    if mhwp_summary_df.empty:
        print("No MHWP data available.")
        return

    # 打印MHWP统计表
    print("\nMHWP Summary (including specialization and number of patients assigned):")
    # print(mhwp_summary_df.to_string(index=False))
    print(tabulate(mhwp_summary_df, headers='keys', tablefmt='grid', showindex=False))

def view_patients_for_mhwp():
    while True:
        try:
            print("Please enter whose patient you would like to see.")
            mhwp_name = input("Please type the name of MHWP or enter '0' to exit: ")

            # 用户输入0时退出
            if mhwp_name == "0":
                print("Exiting patient view.")
                break  # Exit the loop and return to main menu

                # 确保用户输入非空且格式有效
            if not mhwp_name:
                print("Error: MHWP name cannot be empty. Please try again.")
                continue

                # 获取所有MHWP名称并进行验证，确保用户输入的MHWP名称有效
            mhwp_data = load_mhwp()  # 假设加载的MHWP数据包含所有可用的MHWP
            valid_mhwp_names = mhwp_data['username'].tolist()

                # 检查用户输入的MHWP名称是否存在于有效名称列表中
            if mhwp_name not in valid_mhwp_names:
                print(f"Error: '{mhwp_name}' is not a valid MHWP. Please enter a valid MHWP name.")
                continue

                # 获取并显示该MHWP的患者信息
            get_patients_for_mhwp(mhwp_name)


        except ValueError as ve:
            print(f"Error: {ve}")  # 捕获异常并输出错误信息
        except Exception as e:
            print(f"An unexpected error occurred: {e}")  # 捕获其他异常并输出错误信息
        # finally:
        #     # 可选择是否继续或退出
        #     print("\nWould you like to see another MHWP's patients?")
        #     continue_choice = input("Enter 'yes' to continue, '0' to exit: ").strip().lower()
        #     if continue_choice == '0':
        #         print("Exiting patient view.")
        #         break  # Exit the loop and return to main menu


if __name__ == '__main__':
    # view_patients_for_mhwp()
    display_mhwp_summary()
    display_booking_summary()
    # get_patients_for_mhwp('hougege')
    # display_summary()
#     appointments = load_appointments()
#     plot_mhwps_distribution(appointments)
#
# # 画出医生预约数量变化图
#     plot_appointment_trends(appointments)
#
# # 画出医生预约状态分布图
#     plot_appointment_status_distribution(appointments)

