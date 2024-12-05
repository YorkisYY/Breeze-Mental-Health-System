import pandas as pd
from tabulate import tabulate
from config import *
import time

def list_all_users(role_type, mhwp_data_path=MHWP_DATA_PATH, patients_data_path=PATIENTS_DATA_PATH):
    """
    Display paginated user list with - / + navigation.
    role_type: 'mhwp' or 'patient'
    Returns selected username or None if cancelled.
    """
    if role_type == 'mhwp':
        df = pd.read_csv(mhwp_data_path)
        headers = ['#', 'Username', 'Status', 'Major']
    else:
        df = pd.read_csv(patients_data_path)
        headers = ['#', 'Username', 'Status', 'Symptoms']
        
    users = df.to_dict('records')
    page_size = 9
    current_page = 0
    total_pages = (len(users) - 1) // page_size + 1
    
    while True:
        print("\033[H\033[J")  # Clear screen
        
        start_idx = current_page * page_size
        page_users = users[start_idx:start_idx + page_size]
        
        table_data = []
        for idx, user in enumerate(page_users, 1):
            if role_type == 'mhwp':
                table_data.append([
                    idx,
                    user['username'],
                    user.get('account_status', 'active'),
                    user.get('major', 'N/A')
                ])
            else:
                table_data.append([
                    idx,
                    user['username'],
                    user.get('account_status', 'active'),
                    user.get('symptoms', 'N/A')
                ])
            
        print(tabulate(table_data, headers=headers, tablefmt='grid'))   
        print(f"User List (Page {current_page + 1}/{total_pages})")
        print("Enter: - previous page, + next page, 0 to cancel, or 1-9 to select user")
             
        choice = input("\nEnter choice: ").strip()
        if not choice:  # Handle empty input
            continue
        
        if choice == '-' and current_page > 0:
            current_page -= 1
        elif choice == '+' and current_page < total_pages - 1:
            current_page += 1
        elif choice.isdigit() and len(choice) == 1 and choice in '123456789':
            idx = int(choice) - 1
            if idx < len(page_users):
                return page_users[idx]['username']
        elif choice == '0':
            return None
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)  # Give users time to read the message
