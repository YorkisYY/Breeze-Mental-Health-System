import pandas as pd
from datetime import datetime
from config import USER_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH

class UserDataManage:  
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