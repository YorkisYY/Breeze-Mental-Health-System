import pandas as pd
import os
from config import MOOD_DATA_PATH, PATIENTS_DATA_PATH

import matplotlib.pyplot as plt
from tabulate import tabulate

from services.patient_records import patient_record_menu


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
        return read_csv(PATIENTS_DATA_PATH)
    except Exception as e:
        print(e)
        return pd.DataFrame() # Returning empty DataFrame in case of an error(make sure the safe of following stage)

# load data from mood
def load_mood_data():
    try:
        return read_csv(MOOD_DATA_PATH)
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


# color_code to color mapping for the pie chart
color_mapping = {
    "Green": "green",
    "Blue": "blue",
    "Yellow": "yellow",
    "Orange": "orange",
    "Red": "red"
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
            plt.xlabel("Time")
            plt.ylabel("Mood Score (1 = Green, 5 = Red)")
            plt.title(f"Mood Trend for {patient_username}")
            # 将时间戳格式化为日期字符串，仅保留日期部分

            formatted_dates = pd.to_datetime(mood_data["timestamp"])
            formatted_dates = formatted_dates.dt.strftime('%Y-%m-%d: %H:%M')

            # 设置 X 轴刻度标签为格式化后的日期，并旋转标签
            plt.xticks(mood_data["timestamp"], formatted_dates, rotation = 45)

            plt.yticks([1, 2, 3, 4, 5])  # 只显示整数标签

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


import numpy as np
import pickle
from services.trainModal import compute_tfidf
# 加载模型
with open('emotion_model.pkl', 'rb') as f:
    model = pickle.load(f)

word_index = model['word_index']
idf = model['idf']
centers = model['centers']


# 新数据情绪识别
def predict_emotion(new_document, word_index, idf, centers):
    # 计算新文档的TF-IDF特征
    new_tfidf = compute_tfidf([new_document], word_index, idf)[0]  # 计算新文档的TF-IDF特征

    # 计算新文档与每个聚类中心的距离
    distances = np.linalg.norm(centers - new_tfidf, axis=1)  # 计算与每个簇中心的距离

    # 找到距离最小的中心
    cluster_id = np.argmin(distances)
    return cluster_id


# 使用已加载的模型进行预测
new_comment = "feeling a bit stressed"
predicted_cluster = predict_emotion(new_comment, word_index, idf, centers)
print(f"Predicted cluster for the new comment: {predicted_cluster}")



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

                # 显示情绪预测
                print("Would you like to predict the patient's mood? (Y/N)")
                predict_choice = input().strip()
                if predict_choice.lower() == "y":
                    try:
                        # 提取最后一个情绪数据并预测

                        last_mood_comment = get_patient_mood_data(patient_name)
                        last_mood_comment = last_mood_comment.iloc[-1]["comments"]
                        predicted_cluster = predict_emotion(last_mood_comment, word_index, idf, centers)
                        mood_labels = ["Green", "Blue", "Yellow", "Orange", "Red"]
                        print(f"Predicted mood for {patient_name}: {mood_labels[predicted_cluster]}")
                    except Exception as e:
                        print(f"Error during prediction: {e}")

                print("Do you want to see more information about the patient?(Y/N)")

                while True:
                    isSee = input()
                    if isSee == "Y":
                        patient_record_menu(patient_name, mhwp_username)
                        break
                    elif isSee == "N":
                        break
                    else:
                        print("Invalid choice, please try again.")


            elif choice == "2":
                print("Returning to main menu.")
                break

            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"Error displaying dashboard: {e}")


if __name__ == '__main__':
    display_dashboard('hougege')
    # plot_mood("houdidi3")
    # patient_record_menu('houdidi3', 'hougege')
