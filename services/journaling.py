import pandas as pd
from datetime import datetime
from config import JOURNAL_ENTRIES_PATH


def enter_journaling(username):
    """
    Allow patients to input journaling and save to CSV file
    """
    print("\nEnter a new journal entry:")
    entry = input("Your journal entry: ").strip()

    if not entry:
        print("No entry provided. Journaling cancelled.")
        return

    # Generate a new record
    new_entry = {
        "patient_username": username,
        "entry": entry,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to journaling.csv
    try:
        journal_df = pd.read_csv(JOURNAL_ENTRIES_PATH)
        journal_df = pd.concat([journal_df, pd.DataFrame([new_entry])], ignore_index=True)
    except FileNotFoundError:
        journal_df = pd.DataFrame([new_entry])

    journal_df.to_csv(JOURNAL_ENTRIES_PATH, index=False)
    print("Your journal entry has been saved successfully!")

