
import pandas as pd
import os




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

# load data from patients
def load_patient_data():
    try:
        return read_csv("../data/patients.csv")
    except Exception as e:
        print(e)
        return pd.DataFrame() # Returning empty DataFrame in case of an error(make sure the safe of following stage)

# load data from mood
def load_mood_data():
    try:
        return read_csv("../data/mood_data.csv")
    except Exception as e:
        print(e)
        return pd.DataFrame() # Returning empty DataFrame in case of an error(make sure the safe of following stage)


def get_patients_by_mhwp(mhwp_username):
    patients = load_patient_data()
    if patients.empty: # In case the file just have Table head without any data rows
        print("No patient data available.")
        return pd.DataFrame()
    return patients[patients["assigned_mhwp"] == mhwp_username]

# more information about patients
def get_patient_mood_data(username):
    moods = load_mood_data()
    if moods.empty: # In case the file just have Table head without any data rows
        print("No mood data available.")
        return pd.DataFrame()
    return moods[moods["username"] == username]

color_code_to_score = {
    "Green": 1,
    "Blue": 2,
    "Yellow": 3,
    "Orange": 4,
    "Red": 5,
}

def generate_summary(mhwp_username):
    try:
        patients = get_patients_by_mhwp(mhwp_username)
        moods = load_mood_data()

        if patients.empty:
            print("No patient data available for summary.")
            return pd.DataFrame()

        summary = []
        for _, patient in patients.iterrows():
            username = patient["username"]
            mood_data = moods[moods["username"] == username] # Mood of one patient

            total_moods = len(mood_data)

            if total_moods == 0:
                last_mood = "N/A"
                average_mood = "N/A"
            else:
                mood_data = mood_data.sort_values(by="timestamp", ascending=False)


                last_mood = mood_data.iloc[0]["color_code"]
                mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)
                average_mood = mood_data["mood_score"].mean()


            summary.append({
                "username": username,
                #"Name": patient["username"],
                #"Appointments": patient["total_appointments"],
                "Mood Entries": total_moods,
                "Last Mood": last_mood,
                "Average Mood Score": average_mood
            })

        return pd.DataFrame(summary)

    except KeyError as e: # In case nonexistent columns
        print(f"Data error: Missing column {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error during summary generation: {e}")
        return pd.DataFrame()


from tabulate import tabulate


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




mhwp_username = 'mhwp_01'
# result = generate_summary(mhwp_username)
# display_patient_summary_tabulate(result)
# display_patient_summary(result)


#print(result)


import matplotlib.pyplot as plt

# color_code to color mapping for the pie chart
color_mapping = {
    "Green": "green",
    "Blue": "blue",
    "Yellow": "yellow",
    "Orange": "orange",
    "Red": "red"
}

def plot_mood(patient_username):
    try:
        moods = load_mood_data()

        if moods.empty:
            print("No mood data found.")
            return

        mood_data = moods[moods["username"] == patient_username]

            # 如果没有情绪数据，跳过
        if mood_data.empty:
            print(f"No mood data available for patient {patient_username}.")
            return
            # 按时间排序情绪数据
        mood_data = mood_data.sort_values(by="timestamp", ascending=True)

            # 将颜色码映射为评分
        mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)


        try:    # 画出情绪评分的折线图
            plt.figure(figsize=(10, 5))
            plt.plot(mood_data["timestamp"], mood_data["mood_score"], label=f"{patient_username}'s Mood Trend",
                    marker='o')
            plt.xlabel("Timestamp")
            plt.ylabel("Mood Score (1 = Green, 5 = Red)")
            plt.title(f"Mood Trend for {patient_username}")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error while plotting mood trend: {e}")

        try:
            #显示情绪状态分布的饼图
            mood_counts = mood_data["color_code"].value_counts()
            # 使用颜色映射将每个情绪状态对应颜色
            colors = [color_mapping.get(x) for x in mood_counts.index]
            plt.figure(figsize=(7, 7))
            mood_counts.plot(kind='pie', autopct='%1.1f%%',
                             colors=colors,
                             startangle=90, counterclock=False)  # startangle设置起始角度
            plt.title("Mood Status Distribution")
            plt.ylabel("")  # 去掉y轴标签
            plt.show()
        except Exception as e:
            print(f"Error while generating mood pie chart: {e}")



    except Exception as e:
        print(f"Error while generating mood trend plots: {e}")

# def plot_mood_tracking(patient_id, patient_name):
#     try:
#
#
#
#         mood_data = get_patient_mood_data(patient_id)
#         if mood_data.empty:
#             print(f"No mood data available for {patient_name}.")
#             return
#
#         # Make sure the date field exists and is formatted correctly
#         if "date" not in mood_data.columns or "color_code" not in mood_data.columns:
#             print(f"Invalid data for patient {patient_name}. Skipping plot.")
#             return
#
#         # Check and process the date format
#         # Check and process the date format
#         # Check and process the date format
#         # Check and process the date format
#         try:
#             mood_data["date"] = pd.to_datetime(mood_data["date"])
#         except Exception:
#             print(f"Error parsing dates for patient {patient_name}. Skipping plot.")
#             return
#
#         mood_data = mood_data.sort_values(by="timestamp", ascending=True)
#         mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)
#
#
#         plt.figure(figsize=(10, 6))
#         plt.plot(
#             mood_data["timestamp"], mood_data["mood_score"],
#             marker="o", label=f"{patient_id}'s Mood Trend")
#         plt.title(f"Mood Tracking for {patient_id}")
#         plt.xlabel("Date")
#         plt.ylabel("Mood Score (1 = Green, 5 = Red)")
#         # plt.xticks(rotation=45)
#         plt.grid()
#         plt.legend()
#         # plt.tight_layout()
#         plt.show()
#
#         # 显示情绪状态分布的饼图
#         mood_counts = mood_data["color_code"].value_counts()
#         plt.figure(figsize=(7, 7))
#         mood_counts.plot(kind='pie', autopct='%1.1f%%',
#                          colors=["Green", "Blue", "Yellow", "Orange", "Red"])
#         plt.title("Mood Status Distribution")
#         plt.ylabel("")  # 去掉y轴标签
#         plt.show()
#
#     except Exception as e:
#         print(f"Error generating chart for patient {patient_name}: {e}")
#
#
# def plot_patient_mood_trends(mhwp_username):
#     try:
#         # 获取患者的数据
#         patients = get_patients_by_mhwp(mhwp_username)
#         moods = load_mood_data()
#
#         # 如果没有患者数据，返回
#         if patients.empty:
#             print("No patient data available for summary.")
#             return
#
#         for _, patient in patients.iterrows():
#             patient_username = patient["username"]
#             mood_data = moods[moods["username"] == patient_username]
#
#             # 如果没有情绪数据，跳过
#             if mood_data.empty:
#                 continue
#
#             # 按时间排序情绪数据
#             mood_data = mood_data.sort_values(by="timestamp", ascending=True)
#
#             # 将颜色码映射为评分
#             mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)
#
#             # 画出情绪评分的折线图
#             plt.figure(figsize=(10, 5))
#             plt.plot(mood_data["timestamp"], mood_data["mood_score"], label=f"{patient['username']}'s Mood Trend",
#                      marker='o')
#             plt.xlabel("Timestamp")
#             plt.ylabel("Mood Score (1 = Green, 6 = Brownish Red)")
#             plt.title(f"Mood Trend for {patient['username']}")
#             plt.xticks(rotation=45)
#             plt.legend()
#             plt.tight_layout()
#             plt.show()
#
#         # 显示情绪状态分布的饼图
#         # mood_counts = moods["color_code"].value_counts()
#         # plt.figure(figsize=(7, 7))
#         # mood_counts.plot(kind='pie', autopct='%1.1f%%',
#         #                  colors=["Green", "Blue", "Yellow", "Orange", "Red"])
#         # plt.title("Mood Status Distribution")
#         # plt.ylabel("")  # 去掉y轴标签
#         # plt.show()
#
#         try:
#             # 统计不同颜色代码的出现次数
#             mood_counts = moods["color_code"].value_counts()
#
#             # 绘制饼图
#             plt.figure(figsize=(7, 7))
#             mood_counts.plot(kind='pie', autopct='%1.1f%%',
#                              colors=["green", "blue", "yellow", "orange", "red"],
#                              startangle=90, counterclock=False)  # startangle设置起始角度
#             plt.title("Mood Status Distribution")
#             plt.ylabel("")  # 去掉y轴标签
#             plt.show()
#
#         except Exception as e:
#             print(f"Error while generating mood trend plots: {e}")
#
#
#     except Exception as e:
#         print(f"Error while generating mood trend plots: {e}")
#

def display_dashboard(mhwp_username):
    try:
        summary = generate_summary(mhwp_username)
        if summary.empty:
            print("No summary data available.")
            return

        display_patient_summary_tabulate(summary)

        while True:
            print(f"\nDo you want to see specific patient details or exit the dashboard?")
            print("1. See specific patient details")
            print("2. Returning to main menu")

            choice = input("Select an option (1-2): ").strip()
            if choice == "1":
                patient_name = input("Please type in the username of the patient:").strip()
                plot_mood(patient_name)

            elif choice == "2":
                print("Returning to main menu.")
                break

            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"Error displaying dashboard: {e}")

#display_dashboard(mhwp_username)


#
# def dashboard_menu(mhwp_username):
#     """
#     show menu of dashboard。
#     """
#     summary = generate_summary(mhwp_username)
#     display_patient_summary_tabulate(summary)
#     print("The summary of your patients:")
#     print(summary)
#     while True:
#         print(f"\nMHWP: {mhwp_username}")
#         print("1. waiting")
#         print("2. waiting")
#         print("3. waiting")
#         print("4. waiting")
#         print("5. waiting")
#
#         choice = input("Select an option (1-5): ").strip()
#         if choice == "1":
#             print('waiting')
#         elif choice == "2":
#             print('waiting')
#         elif choice == "3":
#             print('waiting')
#         elif choice == "4":
#             print('waiting')
#         elif choice == "5":
#             print("Returning to main menu.")
#             break
#         else:
#             print("Invalid choice, please try again.")