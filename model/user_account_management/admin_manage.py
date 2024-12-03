import pandas as pd
from config import USER_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH
from .user_update import UserUpdate

class AdminManage:
    def admin_update_user(self, target_username, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        if self.role != "admin":
            print("Only admin users can update others.")
            return False

        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            if target_username not in user_df['username'].values:
                print("Target user does not exist.")
                return False

            user_role = user_df.loc[user_df['username'] == target_username, 'role'].iloc[0]
            current_username = target_username
            changes_made = False

            # Update username
            if new_username and new_username != target_username:
                if new_username in user_df['username'].values:
                    print("New username is already in use.")
                    return False
                
                if not self.update_username_in_files(target_username, new_username, user_role):
                    return False
                current_username = new_username
                changes_made = True

            # Update email
            if new_email:
                if not self.update_email_in_files(current_username, new_email, user_role):
                    return False
                changes_made = True

            # Update emergency email
            if new_emergency_email:
                if not self.update_emergency_email_in_files(current_username, new_emergency_email, user_role):
                    return False
                changes_made = True

            if changes_made:
                return True
            print("No changes were made.")
            return True

        except Exception as e:
            print(f"Error in admin update: {str(e)}")
            return False

    def admin_delete_user(self, username):
        if self.role != "admin":
            print("Only admin users can delete others.")
            return False

        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            if username not in user_df['username'].values:
                print("User does not exist.")
                return False
            
            target_role = user_df[user_df['username'] == username]['role'].values[0]
            if self.delete_user_from_files(username, target_role):
                print(f"User '{username}' deleted successfully by admin.")
                return True
            return False

        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False