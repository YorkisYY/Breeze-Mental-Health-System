import pandas as pd
import hashlib
from config import USER_DATA_PATH
from config import PATIENTS_DATA_PATH
from config import MHWP_DATA_PATH
from datetime import datetime
class User:
    def __init__(self, username, password, role, email=None, emergency_email=None, symptoms=None, major=None):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.email = email
        self.emergency_email = emergency_email
        self.medical_records = []
        self.appointments = []
        self.symptoms = symptoms
        self.major = major
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    def save_to_csv(self):
        try:
            # Load user data
            try:
                user_df = pd.read_csv(USER_DATA_PATH)
                user_df['email'] = user_df['email'].astype(str)
                user_df['emergency_email'] = user_df['emergency_email'].astype(str)

                if self.username in user_df['username'].values:
                    print("Username has been used. Please choose a different one.")
                    return False
            except FileNotFoundError:
                user_df = pd.DataFrame(columns=["username", "password", "role", "email", "emergency_email"])

            # Add new user to user_data.csv
            new_user = pd.DataFrame({
                "username": [self.username],
                "password": [self.password],
                "role": [self.role],
                "email": [self.email if self.email else ""],
                "emergency_email": [self.emergency_email if self.emergency_email else ""]
            })
            user_df = pd.concat([user_df, new_user], ignore_index=True)
            user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')

            # Initialize patient record only if role is 'patient' and record does not exist
            if self.role == "patient" and not self.check_patient_record_exists():
                self.initialize_patient_record()
            # Initialize MHWP record only if role is 'mhwp' and record does not exist
            elif self.role == "mhwp" and not self.check_mhwp_record_exists():
                self.initialize_mhwp_record()

            return True
        except Exception as e:
            print(f"Error saving user data: {str(e)}")
            return False
    def load_from_csv(self):
        """Load user data from CSV and update object state."""
        try:
            # Load user data
            df = pd.read_csv(USER_DATA_PATH)
            user_info = df[df['username'] == self.username]
            
            if not user_info.empty:
                stored_password = user_info.iloc[0]['password']
                if stored_password != self.password:
                    print("Incorrect password.")
                    return False
                    
                self.role = user_info.iloc[0]['role']
                self.email = user_info.iloc[0]['email']
                self.emergency_email = user_info.iloc[0]['emergency_email']
                
                # If user is a patient, load patient record
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        patient_info = patient_df[patient_df['username'] == self.username]
                        if not patient_info.empty:
                            self.assigned_mhwp = patient_info.iloc[0]['assigned_mhwp']
                            self.account_status = patient_info.iloc[0]['account_status']
                            self.registration_date = patient_info.iloc[0]['registration_date']
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        return False
                # If user is a MHWP, load MHWP record
                elif self.role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv("data/mhwp.csv")
                        mhwp_info = mhwp_df[mhwp_df['username'] == self.username]
                        if not mhwp_info.empty:
                            self.assigned_patients = mhwp_info.iloc[0]['assigned_patients']
                            self.account_status = mhwp_info.iloc[0]['account_status']
                            self.registration_date = mhwp_info.iloc[0]['registration_date']
                            self.major = mhwp_info.iloc[0]['major']
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        return False
                return True
            return False
        except FileNotFoundError:
            print("User data file not found.")
            return False

    def check_if_exists(self):
        """Check if user exists in CSV."""
        try:
            df = pd.read_csv(USER_DATA_PATH)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False
    def check_patient_record_exists(self, patient_data_path=PATIENTS_DATA_PATH):
        """Check if the patient record already exists."""
        try:
            df = pd.read_csv(patient_data_path)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False
    def check_mhwp_record_exists(self, mhwp_data_path=MHWP_DATA_PATH):
        """Check if the MHWP record already exists."""
        try:
            df = pd.read_csv(mhwp_data_path)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False
        
    def update_info(self, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        """Update user information and synchronize with user_data.csv and patients.csv."""
        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            old_username = self.username
            changes_made = False
            messages = []

            # Update username
            if new_username and new_username != old_username:
                if new_username in user_df['username'].values:
                    messages.append("New username is already in use.")
                else:
                    user_df.loc[user_df['username'] == old_username, 'username'] = new_username
                    if not self.update_username_in_files(old_username, new_username, self.role):
                        messages.append("Error updating username in related files.")
                        return False
                    self.username = new_username
                    changes_made = True
                    messages.append(f"Username successfully updated to: {new_username}")

            # Update password
            if new_password:
                hashed_new_password = self.hash_password(new_password)
                if hashed_new_password == self.password:
                    messages.append("New password is the same as the current one. No changes made.")
                else:
                    user_df.loc[user_df['username'] == self.username, 'password'] = hashed_new_password
                    self.password = hashed_new_password
                    changes_made = True
                    messages.append("Password updated successfully.")

            # Update email
            if new_email:
                user_df.loc[user_df['username'] == self.username, 'email'] = new_email
                self.email = new_email
                changes_made = True
                messages.append(f"Email updated to: {new_email}")

            # Update emergency email
            if new_emergency_email:
                user_df.loc[user_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                self.emergency_email = new_emergency_email
                changes_made = True
                messages.append(f"Emergency email updated to: {new_emergency_email}")

            # Save changes if any
            if changes_made:
                user_df.to_csv(USER_DATA_PATH, index=False)
                messages.append("All changes saved successfully.")
            else:
                messages.append("No changes were made.")

            # Print all messages at once
            for msg in messages:
                print(msg)
            return True

        except Exception as e:
            print(f"Error in update process: {str(e)}")
            return False

                
    def delete_user(self):
        """Delete user from CSV files."""
        if not self.load_from_csv():
            print("User does not exist.")
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



    def delete_from_csv(self):
        """Delete user from user_data.csv and patients.csv if applicable."""
        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            user_df = user_df[user_df['username'] != self.username]
            user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
            
            if self.role == "patient":
                try:
                    patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                    patient_df = patient_df[patient_df['username'] != self.username]
                    patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                    print("Patient record deleted successfully.")
                except FileNotFoundError:
                    print("Patient data file not found. Skipping patient record deletion.")
                except Exception as e:
                    print(f"Error deleting patient record: {str(e)}")

            print("User deleted successfully.")
        except FileNotFoundError:
            print("User data file not found.")
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            
    def admin_update_user(self, target_username, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        """Admin method to update other users' information."""
        if self.role != "admin":
            print("Only admin users can update others.")
            return False

        try:
            # Load user_data.csv
            user_df = pd.read_csv(USER_DATA_PATH)
            
            if target_username not in user_df['username'].values:
                print("Target user does not exist.")
                return False
            
            changes_made = False
            user_role = user_df.loc[user_df['username'] == target_username, 'role'].iloc[0]

            # Update username
            if new_username and new_username != target_username:
                if new_username in user_df[user_df['username'] != target_username]['username'].values:
                    print("New username is already in use.")
                    return False

                if not self.update_username_in_files(target_username, new_username, user_role):
                    return False
                
                changes_made = True
                print(f"Username updated to '{new_username}'.")
                # Update role-specific records
                if user_role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        if target_username in patient_df['username'].values:
                            patient_df.loc[patient_df['username'] == target_username, 'username'] = new_username
                            patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                            print("Patient record username updated successfully.")
                    except Exception as e:
                        print(f"Error updating patient username: {str(e)}")
                        return False
                elif user_role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                        if target_username in mhwp_df['username'].values:
                            mhwp_df.loc[mhwp_df['username'] == target_username, 'username'] = new_username
                            mhwp_df.to_csv(MHWP_DATA_PATH, index=False)
                            print("MHWP record username updated successfully.")
                    except Exception as e:
                        print(f"Error updating MHWP username: {str(e)}")
                        return False

            current_username = new_username if new_username else target_username

            # Update password
            if new_password:
                hashed_new_password = self.hash_password(new_password)
                current_password = user_df.loc[user_df['username'] == current_username, 'password'].iloc[0]
                if hashed_new_password == current_password:
                    print("New password is the same as the current one.")
                else:
                    user_df.loc[user_df['username'] == current_username, 'password'] = hashed_new_password
                    changes_made = True
                    print("Password updated successfully.")

            # Update email
            if new_email:
                user_df.loc[user_df['username'] == current_username, 'email'] = new_email
                changes_made = True
                print(f"Email updated to '{new_email}'.")

                if user_role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        if current_username in patient_df['username'].values:
                            patient_df.loc[patient_df['username'] == current_username, 'email'] = new_email
                            patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating patient email: {str(e)}")
                elif user_role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                        if current_username in mhwp_df['username'].values:
                            mhwp_df.loc[mhwp_df['username'] == current_username, 'email'] = new_email
                            mhwp_df.to_csv(MHWP_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating MHWP email: {str(e)}")

            # Update emergency email
            if new_emergency_email:
                user_df.loc[user_df['username'] == current_username, 'emergency_email'] = new_emergency_email
                changes_made = True
                print(f"Emergency email updated to '{new_emergency_email}'.")

                if user_role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        if current_username in patient_df['username'].values:
                            patient_df.loc[patient_df['username'] == current_username, 'emergency_email'] = new_emergency_email
                            patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating patient emergency email: {str(e)}")
                elif user_role == "mhwp":
                    try:
                        mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                        if current_username in mhwp_df['username'].values:
                            mhwp_df.loc[mhwp_df['username'] == current_username, 'emergency_email'] = new_emergency_email
                            mhwp_df.to_csv(MHWP_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating MHWP emergency email: {str(e)}")

            if changes_made:
                user_df.to_csv(USER_DATA_PATH, index=False)
                print("Admin update completed successfully.")
                return True

            print("No changes were made.")
            return True

        except Exception as e:
            print(f"Error in admin update: {str(e)}")
            return False
    def display_info(self):
        """Display user information."""
        print(f"Username: {self.username}, Role: {self.role}")
        
    def admin_delete_user(self, username):
        """Admin method to delete a user and their associated record if applicable."""
        if self.role != "admin":
            print("Only admin users can delete others.")
            return False

        try:
            # Load user_data.csv
            user_df = pd.read_csv(USER_DATA_PATH)
            
            # Check if the target user exists
            if username not in user_df['username'].values:
                print("User does not exist.")
                return False
            
            # Check if the target user is a patient and delete from patients.csv if necessary
            target_role = user_df[user_df['username'] == username]['role'].values[0]
            if target_role == "patient":
                try:
                    patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                    if username in patient_df['username'].values:
                        patient_df = patient_df[patient_df['username'] != username]
                        patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                        print("Patient record deleted successfully.")
                except FileNotFoundError:
                    print("Patient data file not found. Skipping patient record deletion.")
                except Exception as e:
                    print(f"Error deleting patient record: {str(e)}")
            # Check if the target user is a MHWP and delete from mhwp.csv if necessary
            elif target_role == "mhwp":
                try:
                    mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                    if username in mhwp_df['username'].values:
                        mhwp_df = mhwp_df[mhwp_df['username'] != username]
                        mhwp_df.to_csv(MHWP_DATA_PATH, index=False, na_rep='')
                        print("MHWP record deleted successfully.")
                except FileNotFoundError:
                    print("MHWP data file not found. Skipping MHWP record deletion.")
                except Exception as e:
                    print(f"Error deleting MHWP record: {str(e)}")

            # Delete the user from user_data.csv
            user_df = user_df[user_df['username'] != username]
            user_df.to_csv(USER_DATA_PATH, index=False, na_rep='')
            print(f"User '{username}' deleted successfully by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False

    def initialize_patient_record(self, patient_data_path=PATIENTS_DATA_PATH):
        """Initialize patient record with complete user information."""
        if self.role != "patient":
            print("Only patients can have patient records.")
            return False

        try:
            if self.check_patient_record_exists():
                print("Patient record already exists.")
                return False
            
            try:
                df = pd.read_csv(patient_data_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=[
                    "username", "assigned_mhwp", "account_status",
                    "registration_date", "email", "emergency_email", "symptoms"
                ])

            new_patient = pd.DataFrame({
                "username": [self.username],
                "assigned_mhwp": [""],
                "account_status": ["active"],  
                "registration_date": [datetime.now().strftime("%Y-%m-%d")],
                "email": [self.email if self.email else ""],
                "emergency_email": [self.emergency_email if self.emergency_email else ""],
                "symptoms": [self.symptoms if self.symptoms else ""]
            })

            df = pd.concat([df, new_patient], ignore_index=True)
            df.to_csv(patient_data_path, index=False, na_rep='')
            print("Patient record initialized successfully.")
            return True

        except Exception as e:
            print(f"Error creating patient record: {str(e)}")
            return False
    def initialize_mhwp_record(self, mhwp_data_path="data/mhwp.csv"):
        """Initialize MHWP record with complete user information."""
        if self.role != "mhwp":
            print("Only MHWPs can have MHWP records.")
            return False

        try:
            if self.check_mhwp_record_exists():
                print("MHWP record already exists.")
                return False
            
            try:
                df = pd.read_csv(mhwp_data_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=[
                    "username", "assigned_patients", "account_status",
                    "registration_date", "email", "emergency_email", "major"
                ])

            new_mhwp = pd.DataFrame({
                "username": [self.username],
                "assigned_patients": [""],
                "account_status": ["active"],
                "registration_date": [datetime.now().strftime("%Y-%m-%d")],
                "email": [self.email if self.email else ""],
                "emergency_email": [self.emergency_email if self.emergency_email else ""],
                "major": [self.major if self.major else ""]
            })

            df = pd.concat([df, new_mhwp], ignore_index=True)
            df.to_csv(mhwp_data_path, index=False, na_rep='')
            print("MHWP record initialized successfully.")
            return True

        except Exception as e:
            print(f"Error creating MHWP record: {str(e)}")
            return False
        
    def update_patient_mhwp(self, patient_username, mhwp_username, patient_data_path="data/patients.csv"):
        """Admin function to assign or update MHWP for a patient"""
        if self.role != "admin":
            print("Only admin can assign MHWPs to patients.")
            return False
            
        try:
            df = pd.read_csv(patient_data_path)
            if patient_username not in df['username'].values:
                print("Patient record not found.")
                return False
                
            df.loc[df['username'] == patient_username, 'assigned_mhwp'] = mhwp_username
            df.to_csv(patient_data_path, index=False)
            print(f"MHWP {mhwp_username} assigned to patient {patient_username}")
            return True
            
        except Exception as e:
            print(f"Error updating patient's MHWP: {str(e)}")
            return False

    def update_patient_status(self, patient_username, status, patient_data_path="data/patients.csv"):
        """Admin function to freeze/unfreeze patient account"""
        if self.role != "admin":
            print("Only admin can update patient status.")
            return False
            
        if status not in ['yes', 'no']:
            print("Invalid status. Use 'yes' for frozen or 'no' for active.")
            return False
            
        try:
            df = pd.read_csv(patient_data_path)
            if patient_username not in df['username'].values:
                print("Patient record not found.")
                return False
                
            df.loc[df['username'] == patient_username, 'account_status'] = status
            df.to_csv(patient_data_path, index=False)
            status_text = "frozen" if status == "yes" else "activated"
            print(f"Patient account {patient_username} has been {status_text}")
            return True
            
        except Exception as e:
            print(f"Error updating patient status: {str(e)}")
            return False
    def update_mhwp_major(self, mhwp_username, major, mhwp_data_path="data/mhwp.csv"):
        """Admin function to update MHWP's major"""
        if self.role != "admin":
            print("Only admin can update MHWP major.")
            return False
            
        try:
            df = pd.read_csv(mhwp_data_path)
            if mhwp_username not in df['username'].values:
                print("MHWP record not found.")
                return False
                
            df.loc[df['username'] == mhwp_username, 'major'] = major
            df.to_csv(mhwp_data_path, index=False)
            print(f"Major updated for MHWP {mhwp_username}")
            return True
            
        except Exception as e:
            print(f"Error updating MHWP major: {str(e)}")
            return False

    def update_mhwp_status(self, mhwp_username, status, mhwp_data_path="data/mhwp.csv"):
        """Admin function to update MHWP account status"""
        if self.role != "admin":
            print("Only admin can update MHWP status.")
            return False
            
        if status not in ['active', 'inactive']:
            print("Invalid status. Use 'active' or 'inactive'.")
            return False
            
        try:
            df = pd.read_csv(mhwp_data_path)
            if mhwp_username not in df['username'].values:
                print("MHWP record not found.")
                return False
                
            df.loc[df['username'] == mhwp_username, 'account_status'] = status
            df.to_csv(mhwp_data_path, index=False)
            print(f"MHWP account {mhwp_username} status updated to {status}")
            return True
            
        except Exception as e:
            print(f"Error updating MHWP status: {str(e)}")
            return False
    def update_username_in_files(self, old_username, new_username, role):
        """Update username in all relevant files."""
        try:
            # Mapping of files and fields to update
            updates = {
                'user_data.csv': ['username'],
                'patients.csv': ['username', 'assigned_mhwp'] if role == 'mhwp' else None,
                'mhwp.csv': ['username', 'assigned_patients'] if role == 'mhwp' else None,
                'mood_data.csv': ['username'] if role == 'patient' else None,  
                'appointments.csv': ['patient_username', 'mhwp_username'],
                'assignments.csv': ['patient_username', 'mhwp_username'],
                'comments.csv': ['patient_username', 'mhwp_username'],
                'mental_assessments.csv': ['patient_username', 'mhwp_username'],
                'patient_journaling.csv': ['patient_username'] if role == 'patient' else None,
                'patient_notes.csv': ['patient_username', 'mhwp_username'],
                'mhwp_schedule.csv': ['mhwp_username'] if role == 'mhwp' else None
            }

            log = [] 

            # Iterate over each file and update relevant fields
            for file, columns in updates.items():
                if columns:
                    try:
                        file_path = f"data/{file}"
                        df = pd.read_csv(file_path)

                        # Update each relevant column
                        for column in columns:
                            if column in df.columns:
                                df.loc[df[column] == old_username, column] = new_username
                                log.append(f"Updated {column} in {file}")
                            else:
                                log.append(f"Column {column} not found in {file}")

                        # Save updated DataFrame
                        df.to_csv(file_path, index=False)
                    except FileNotFoundError:
                        log.append(f"File {file} not found. Skipping.")
                    except Exception as e:
                        log.append(f"Error updating {file}: {str(e)}")
            
            # Print the update log for debugging
            for entry in log:
                print(entry)

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