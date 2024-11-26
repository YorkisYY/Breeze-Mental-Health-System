import pandas as pd
from datetime import datetime

COMMENTS_FILE = "data/comments.csv"

def add_comment(patient_username, mhwp_username, comment):
    """
    添加评论到评论文件。
    """
    try:
        # 准备评论数据
        comment_data = {
            "patient_username": patient_username,
            "mhwp_username": mhwp_username,
            "comment": comment,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 读取或创建评论文件
        try:
            comments_df = pd.read_csv(COMMENTS_FILE)
            comments_df = comments_df.append(comment_data, ignore_index=True)
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
            print("Patient      | Comment                               | Timestamp")
            print("------------------------------------------------------------------")
            for _, row in mhwp_comments.iterrows():
                print(f"{row['patient_username']:<12} | {row['comment']:<40} | {row['timestamp']}")
            print("------------------------------------------------------------------")

    except FileNotFoundError:
        print("No comments file found. Please initialize it first.")
    except Exception as e:
        print(f"Error viewing comments: {e}")
