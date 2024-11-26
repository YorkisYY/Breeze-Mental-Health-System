import pandas as pd
from datetime import datetime

JOURNAL_FILE = "data/journal_entries.csv"

def enter_journaling(username):
    """
    让患者输入 Journaling 并存储到 CSV 文件
    """
    print("\nEnter a new journal entry:")
    entry = input("Your journal entry: ").strip()

    if not entry:
        print("No entry provided. Journaling cancelled.")
        return

    # 生成新记录
    new_entry = {
        "username": username,
        "entry": entry,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 保存到 journaling.csv
    try:
        journal_df = pd.read_csv(JOURNAL_FILE)
        journal_df = journal_df.append(new_entry, ignore_index=True)
    except FileNotFoundError:
        journal_df = pd.DataFrame([new_entry])

    journal_df.to_csv(JOURNAL_FILE, index=False)
    print("Your journal entry has been saved successfully!")
