import pandas as pd
from datetime import datetime


COMMENTS_FILE = "data/comments.csv"
APPOINTMENTS_FILE = "data/appointments.csv"


def comment(patient_username):
    """
    提供评论功能，基于登录用户的用户名获取预约信息。
    """
    available_appointments, option_map = get_available_appointments(patient_username)

    if not available_appointments.empty:
        try:
            # 用户输入 Option
            option = int(input("Select an appointment option to comment on (1, 2, ...): "))

            # 检查 Option 是否有效
            if option not in option_map:
                print("Invalid option selected.")
                return

            # 使用 Option 找到对应的 DataFrame 行
            selected_appointment = available_appointments.iloc[option_map[option]]
            appointment_id = selected_appointment["id"]
            mhwp_username = selected_appointment["mhwp_username"]
            appointment_datetime = selected_appointment["datetime"].strftime("%Y-%m-%d %H:%M:%S")

            # 获取评论信息
            rating = float(input("Enter your rating (0-5): "))
            comment_text = input("Enter your comment: ")

            # 添加评论
            add_comment(patient_username, mhwp_username, rating, comment_text, appointment_id, appointment_datetime)
        except ValueError:
            print("Invalid input. Please select a valid option.")

            
            
def add_comment(patient_username, mhwp_username, rating, comment, appointment_id, appointment_datetime):
    """
    添加患者对 MHWP 的评价（评分和评论）到评论文件，并绑定具体的预约。
    """
    try:
        # 验证评分范围
        if not (0 <= rating <= 5):
            print("Invalid rating. Please provide a rating between 0 and 5.")
            return

        # 准备评论数据
        comment_data = {
            "patient_username": patient_username,
            "mhwp_username": mhwp_username,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "appointment_id": appointment_id,
            "appointment_datetime": appointment_datetime,
        }

        # 读取或创建评论文件
        try:
            comments_df = pd.read_csv(COMMENTS_FILE)
            
            # 检查是否已对该预约评论
            if not comments_df.empty and appointment_id in comments_df["appointment_id"].values:
                print("You have already commented on this appointment.")
                return

            # 非空情况下，拼接新数据
            comments_df = pd.concat([comments_df, pd.DataFrame([comment_data])], ignore_index=True)
        except FileNotFoundError:
            # 如果文件不存在，则创建新文件
            comments_df = pd.DataFrame([comment_data])

        # 保存评论
        comments_df.to_csv(COMMENTS_FILE, index=False)
        print("Comment added successfully!")

    except Exception as e:
        print(f"Error adding comment: {e}")


def get_available_appointments(patient_username):
    """
    获取患者所有符合评论条件的预约列表。
    条件：status 为 confirmed 且时间已过去。
    """
    try:
        # 读取预约数据
        appointments = pd.read_csv(APPOINTMENTS_FILE)

        # 筛选属于该患者的预约，并创建副本
        patient_appointments = appointments[appointments["patient_username"] == patient_username].copy()

        if patient_appointments.empty:
            print("No appointments found for this patient.")
            return pd.DataFrame()

        # 筛选符合条件的预约
        now = datetime.now()
        patient_appointments["datetime"] = pd.to_datetime(
            patient_appointments["date"] + " " + patient_appointments["timeslot"].str.split("-").str[0]
        )
        available_appointments = patient_appointments[
            (patient_appointments["status"] == "confirmed") & (patient_appointments["datetime"] < now)
        ].reset_index(drop=True)

        if available_appointments.empty:
            print("No appointments available for commenting.")
            return pd.DataFrame()

        # 显示可选预约
        print("\nAvailable appointments for commenting:")
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





def view_comments(mhwp_username):
    """
    查看某 MHWP 的所有评论。
    """
    try:
        # 加载评论文件
        comments_df = pd.read_csv(COMMENTS_FILE)
        
        # 筛选出属于该 MHWP 的评论
        mhwp_comments = comments_df[comments_df["mhwp_username"] == mhwp_username]

        if mhwp_comments.empty:
            print(f"No comments found for MHWP '{mhwp_username}'.")
        else:
            print(f"\nComments for MHWP '{mhwp_username}':")
            print("------------------------------------------------------------------")
            print("Patient      | Rating | Comment                               | Timestamp")
            print("------------------------------------------------------------------")
            for _, row in mhwp_comments.iterrows():
                print(f"{row['patient_username']:<12} | {row['rating']:<6} | {row['comment']:<40} | {row['timestamp']}")
            print("------------------------------------------------------------------")

    except FileNotFoundError:
        print("No comments file found. Please initialize it first.")
    except Exception as e:
        print(f"Error viewing comments: {e}")

