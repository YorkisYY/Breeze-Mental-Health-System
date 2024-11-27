import pandas as pd
from datetime import datetime

COMMENTS_FILE = "data/comments.csv"

def add_comment(patient_username, mhwp_username, rating, comment):
    """
    添加患者对 MHWP 的评价（评分和评论）到评论文件。
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 读取或创建评论文件
        try:
            comments_df = pd.read_csv(COMMENTS_FILE)
            # 如果读取的 DataFrame 是空的，直接用新数据替换
            if comments_df.empty:
                comments_df = pd.DataFrame([comment_data])
            else:
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


def get_mhwp_for_patient(patient_username, file_path="data/appointments.csv"):
    """
    从 appointments.csv 文件中获取患者的 MHWP 用户名。
    """
    try:
        appointments = pd.read_csv(file_path)
        mhwp_record = appointments[appointments["patient_username"] == patient_username]
        if not mhwp_record.empty:
            return mhwp_record.iloc[0]["mhwp_username"]
        else:
            print("No MHWP found for this patient.")
            return None
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
