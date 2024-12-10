import pandas as pd
from config import USER_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH
from .user_update import UserUpdate

class AdminManage:
    def admin_update_user(self, target_username, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        if self.role != "admin":
            print("Only admin users can update others.")
            return False
        # Method for admin to update a user's information
        try:
        # Check whether the username is within the csv or not
            user_df = pd.read_csv(USER_DATA_PATH)
            if target_username not in user_df['username'].values:
                print("Target user does not exist.")
                return False

            user_role = user_df.loc[user_df['username'] == target_username, 'role'].iloc[0]
            current_username = target_username
            changes_made = False

        # The function would simultaneously change the info within user_data.csv and every csv which matches the username.
        # A username would only be allowed to register for a singel role, such as a can't be registered as a MHWP and patient.
            if new_username and new_username != target_username:
                if new_username in user_df['username'].values:
                    print("New username is already in use.")
                    return False
        #call the function within the userupdate.file, searching for all csv
                if not self.update_username_in_files(target_username, new_username, user_role):
                    return False
                current_username = new_username
                changes_made = True
        #the function of updating is only related to username and password so the email and emergency_email would be independent case    
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
        # admin also can delete users, and the information would be deleted from user_data.csv and MHWP.csv or patient.csv.
        # It depends on the character, as our discussion we would like to keep some record
        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            if username not in user_df['username'].values:
                print("User does not exist.")
                return False
                
            target_role = user_df[user_df['username'] == username]['role'].values[0]
            print(f"Deleting {target_role} user: {username}")

            user_df = user_df[user_df['username'] != username]
            user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
            print("Deleted from user_data.csv successfully")

            if target_role == "patient":
                patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                patient_df = patient_df[patient_df['username'] != username]
                patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                    
            elif target_role == "mhwp":
                mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                mhwp_df = mhwp_df[mhwp_df['username'] != username]
                mhwp_df.to_csv(MHWP_DATA_PATH, index=False, na_rep='')
                    
            print(f"User '{username}' and all related records deleted successfully.")
            
            if username == self.username:
                print("You have deleted your own account. Logging out...")
                return "self_deleted"
            return True

        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return False