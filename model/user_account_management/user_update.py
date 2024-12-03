import os
from tabulate import tabulate
import pandas as pd
from .base import UserBase
from config import USER_DATA_PATH
from config import PATIENTS_DATA_PATH
from config import MHWP_DATA_PATH

class UserUpdate:
    def update_username_in_files(self, old_username, new_username, role):
        try:
            updates = {
                'user_data.csv': ['username'],
                'patients.csv': ['assigned_mhwp'] if role == 'mhwp' else['username'] if role == 'patient'else None, 
                'mhwp.csv': ['username'] if role == 'mhwp' else ['assigned_patients'] if role == 'patient' else None,
                'mood_data.csv': ['username'] if role == 'patient' else None,  
                'appointments.csv': ['patient_username', 'mhwp_username'],
                'assignments.csv': ['patient_username', 'mhwp_username'],
                'comments.csv': ['patient_username', 'mhwp_username'],
                'mental_assessments.csv': ['patient_username', 'mhwp_username'],
                'patient_journaling.csv': ['patient_username'] if role == 'patient' else None,
                'patient_notes.csv': ['patient_username', 'mhwp_username'],
                'mhwp_schedule.csv': ['mhwp_username'] if role == 'mhwp' else None
            }

            for file, columns in updates.items():
                if columns:
                    try:
                        file_path = f"data/{file}"
                        df = pd.read_csv(file_path)
                        
                        for column in columns:
                            if column in df.columns:
                                df[column] = df[column].astype(str)
                                df.loc[df[column] == str(old_username), column] = str(new_username)
                                
                        df.to_csv(file_path, index=False)
                    except FileNotFoundError:
                        continue
                        
            return True
        except Exception as e:
            print(f"Error updating files: {str(e)}")
            return False
    def delete_user_from_files(self, username, role):
        try:
            deletes = {
                'user_data.csv': 'username',
                'patients.csv': 'username' if role == 'patient' else None,
                'mhwp.csv': 'username' if role == 'mhwp' else None,
                'patients.csv': 'assigned_mhwp' if role == 'patient' else None,
                'mhwp.csv': 'assigned_patients' if role == 'mhwp' else None,
                'mood_data.csv': 'username' if role == 'patient' else None,
                'appointments.csv': 'patient_username' if role == 'patient' else 'mhwp_username',
                'assignments.csv': 'patient_username' if role == 'patient' else 'mhwp_username',
                'comments.csv': 'patient_username' if role == 'patient' else 'mhwp_username',
                'mental_assessments.csv': 'patient_username' if role == 'patient' else 'mhwp_username',
                'patient_journaling.csv': 'patient_username' if role == 'patient' else None,
                'patient_notes.csv': 'patient_username' if role == 'patient' else 'mhwp_username',
                'mhwp_schedule.csv': 'mhwp_username' if role == 'mhwp' else None
            }

            for file, column in deletes.items():
                if column:
                    try:
                        df = pd.read_csv(f"data/{file}")
                        if column in df.columns:
                            df = df[df[column] != username]
                            df.to_csv(f"data/{file}", index=False)
                    except FileNotFoundError:
                        continue
            return True
        except Exception as e:
            print(f"Error deleting from files: {str(e)}")
            return False
    def update_info(self, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        """Update user information and synchronize with all related files."""
        try:
            # Load user data and verify user exists
            if not self.load_from_csv():
                print("User does not exist.")
                return False

            # Load user_data.csv
            user_df = pd.read_csv(USER_DATA_PATH)
            old_username = self.username
            changes_made = False
            messages = []

            # Convert all columns to string type
            for col in user_df.columns:
                user_df[col] = user_df[col].astype(str)

            # Update username if provided
            if new_username and new_username != old_username:
                if new_username in user_df['username'].values:
                    messages.append("Username has been used. Please choose a different one.")
                    return False
                
                # Update username in user_data.csv
                user_df.loc[user_df['username'] == old_username, 'username'] = new_username
                
                # Update username in other files
                if not self.update_username_in_files(old_username, new_username, self.role):
                    messages.append("Error updating username in related files.")
                    return False
                
                self.username = new_username
                changes_made = True
                messages.append(f"Username successfully updated to: {new_username}")
                # Save changes immediately after username update
                user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')

            # Update password if provided
            if new_password:
                hashed_new_password = self.hash_password(new_password)
                if hashed_new_password == self.password:
                    messages.append("New password is the same as the current one. No changes made.")
                else:
                    user_df.loc[user_df['username'] == self.username, 'password'] = hashed_new_password
                    self.password = hashed_new_password
                    changes_made = True
                    user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
                    messages.append("Password updated successfully.")

            # Update email if provided
            if new_email:
                # Update in user_data.csv
                user_df.loc[user_df['username'] == self.username, 'email'] = new_email
                user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
                
                # Update in role-specific files
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        patient_df['email'] = patient_df['email'].astype(str)
                        if self.username in patient_df['username'].values:
                            patient_df.loc[patient_df['username'] == self.username, 'email'] = new_email
                            patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                    except FileNotFoundError:
                        print("Patient data file not found.")
                elif self.role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                        mhwp_df['email'] = mhwp_df['email'].astype(str)
                        if self.username in mhwp_df['username'].values:
                            mhwp_df.loc[mhwp_df['username'] == self.username, 'email'] = new_email
                            mhwp_df.to_csv(MHWP_DATA_PATH, index=False, na_rep='')
                    except FileNotFoundError:
                        print("MHWP data file not found.")
                
                self.email = new_email
                changes_made = True
                messages.append(f"Email updated to: {new_email}")

            # Update emergency email if provided
            if new_emergency_email:
                # Update in user_data.csv
                user_df.loc[user_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
                
                # Update in role-specific files
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        patient_df['emergency_email'] = patient_df['emergency_email'].astype(str)
                        if self.username in patient_df['username'].values:
                            patient_df.loc[patient_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                            patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                    except FileNotFoundError:
                        print("Patient data file not found.")
                elif self.role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                        mhwp_df['emergency_email'] = mhwp_df['emergency_email'].astype(str)
                        if self.username in mhwp_df['username'].values:
                            mhwp_df.loc[mhwp_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                            mhwp_df.to_csv(MHWP_DATA_PATH, index=False, na_rep='')
                    except FileNotFoundError:
                        print("MHWP data file not found.")
                
                self.emergency_email = new_emergency_email
                changes_made = True
                messages.append(f"Emergency email updated to: {new_emergency_email}")

            if changes_made:
                messages.append("All changes saved successfully.")
            else:
                messages.append("No changes were made.")

            # Print all messages
            for msg in messages:
                print(msg)
            return True

        except Exception as e:
            print(f"Error in update process: {str(e)}")
            return False
    def update_email_in_files(self, username, new_email, role):
        try:
            updates = {
                'user_data.csv': ['email'],
                'patients.csv': ['email'] if role == 'patient' else None,
                'mhwp.csv': ['email'] if role == 'mhwp' else None,
            }

            for file, columns in updates.items():
                if columns:
                    try:
                        file_path = f"data/{file}"
                        df = pd.read_csv(file_path)
                        
                        for column in columns:
                            if column in df.columns:
                                df[column] = df[column].astype(str)
                                df.loc[df['username'] == str(username), column] = str(new_email)
                                
                        df.to_csv(file_path, index=False)
                    except FileNotFoundError:
                        continue
                        
            return True
        except Exception as e:
            print(f"Error updating email in files: {str(e)}")
            return False

    def update_emergency_email_in_files(self, username, new_emergency_email, role):
        try:
            updates = {
                'user_data.csv': ['emergency_email'],
                'patients.csv': ['emergency_email'] if role == 'patient' else None,
                'mhwp.csv': ['emergency_email'] if role == 'mhwp' else None,
            }

            for file, columns in updates.items():
                if columns:
                    try:
                        file_path = f"data/{file}"
                        df = pd.read_csv(file_path)
                        
                        for column in columns:
                            if column in df.columns:
                                df[column] = df[column].astype(str)
                                df.loc[df['username'] == str(username), column] = str(new_emergency_email)
                                
                        df.to_csv(file_path, index=False)
                    except FileNotFoundError:
                        continue
                        
            return True
        except Exception as e:
            print(f"Error updating emergency email in files: {str(e)}")
            return False
    def update_password(self, new_password):
        """Update user password and synchronize with relevant files."""
        if not self.load_from_csv():
            print("User does not exist.")
            return False

        try:
            # Load user_data.csv
            user_df = pd.read_csv(USER_DATA_PATH)

            # Hash the new password
            hashed_new_password = self.hash_password(new_password)
            if hashed_new_password == self.password:
                print("New password is the same as the current one. No changes made.")
                return False

            # Update password in user_data.csv
            user_df.loc[user_df['username'] == self.username, 'password'] = hashed_new_password
            self.password = hashed_new_password
            user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')

            # If the user is a patient, update related fields in patients.csv
            if self.role == "patient":
                try:
                    patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                    if self.username in patient_df['username'].values:
                        patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                except FileNotFoundError:
                    print("Patient data file not found. Skipping patient record update.")
                except Exception as e:
                    print(f"Error updating patient record: {str(e)}")
            # If the user is a MHWP, update related fields in mhwp.csv
            elif self.role == "mhwp":
                try:
                    mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                    if self.username in mhwp_df['username'].values:
                        mhwp_df.to_csv(MHWP_DATA_PATH, index=False, na_rep='')
                except FileNotFoundError:
                    print("MHWP data file not found. Skipping MHWP record update.")
                except Exception as e:
                    print(f"Error updating MHWP record: {str(e)}")

            print("User password updated successfully.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False