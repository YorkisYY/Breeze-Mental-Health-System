import pandas as pd
import hashlib
from config import USER_DATA_PATH
from config import PATIENTS_DATA_PATH
from datetime import datetime
class User:
    def __init__(self, username, password, role, email=None, emergency_email=None):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.email = email
        self.emergency_email = emergency_email
        self.medical_records = []
        self.appointments = []
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
                
                # If user is a patient, also load patient record
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
    def update_info(self, new_username=None, new_password=None, new_email=None, new_emergency_email=None):
        """Update user information and synchronize with user_data.csv and patients.csv."""
        try:
            user_df = pd.read_csv(USER_DATA_PATH)
            old_username = self.username
            changes_made = False

            if new_username and new_username != old_username:
                if new_username in user_df['username'].values:
                    print("New username is already in use.")
                    return False
                    
                updated_user_df = user_df.copy()
                updated_user_df.loc[updated_user_df['username'] == old_username, 'username'] = new_username
                
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        updated_patient_df = patient_df.copy()
                        updated_patient_df.loc[updated_patient_df['username'] == old_username, 'username'] = new_username
                        updated_patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating patient record: {str(e)}")
                        return False
                
                updated_user_df.to_csv(USER_DATA_PATH, index=False)
                self.username = new_username
                changes_made = True
                print(f"Username successfully updated to: {new_username}")


            if new_password:
                hashed_new_password = self.hash_password(new_password)
                user_df.loc[user_df['username'] == self.username, 'password'] = hashed_new_password
                user_df.to_csv(USER_DATA_PATH, index=False)
                self.password = hashed_new_password
                changes_made = True


            if new_email:
                user_df.loc[user_df['username'] == self.username, 'email'] = new_email
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        patient_df.loc[patient_df['username'] == self.username, 'email'] = new_email
                        patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating patient email: {str(e)}")
                        return False
                user_df.to_csv(USER_DATA_PATH, index=False)
                self.email = new_email
                changes_made = True


            if new_emergency_email:
                user_df.loc[user_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                if self.role == "patient":
                    try:
                        patient_df = pd.read_csv(PATIENTS_DATA_PATH)
                        patient_df.loc[patient_df['username'] == self.username, 'emergency_email'] = new_emergency_email
                        patient_df.to_csv(PATIENTS_DATA_PATH, index=False)
                    except Exception as e:
                        print(f"Error updating patient emergency email: {str(e)}")
                        return False
                user_df.to_csv(USER_DATA_PATH, index=False)
                self.emergency_email = new_emergency_email
                changes_made = True

            return changes_made

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
                        # Patients.csv may not have a password field; ensure it is updated only in user_data.csv.
                        # Update related info in patients.csv if necessary (optional, can extend functionality here).
                        patient_df.to_csv(PATIENTS_DATA_PATH, index=False, na_rep='')
                except FileNotFoundError:
                    print("Patient data file not found. Skipping patient record update.")
                except Exception as e:
                    print(f"Error updating patient record: {str(e)}")

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

                other_users = user_df[user_df['username'] != target_username]
                if new_username in other_users['username'].values:
                    print("New username is already in use.")
                    return False
                

                user_df.loc[user_df['username'] == target_username, 'username'] = new_username
                changes_made = True
                print(f"Username updated to '{new_username}'.")


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

            if changes_made:

                user_df.to_csv(USER_DATA_PATH, index=False)
                print("Admin update completed successfully.")
                return True

            print("No changes were made.")
            return True

        except Exception as e:
            print(f"Error in admin update: {str(e)}")
            return False
<<<<<<< HEAD

=======
        
>>>>>>> 05147549f0b7bc4e4b42355e50ed84cc0044c1c2
    def book_appointment(self, mhwp_username, date, start_time, end_time, user_data_file, schedule_file, appointment_file):
        """
        Allow a patient to book an appointment with an MHW.
        Ensures the booked time is within the MHW's scheduled time and does not overlap with existing appointments.
        """
        if self.role != "patient":
            print("Only patients can book appointments.")
            return False

        try:
            # Verify MHW existence and role from user_data.csv
            try:
                user_data = pd.read_csv(user_data_file)
                mhwp_record = user_data[(user_data['username'] == mhwp_username) & (user_data['role'] == 'mhwp')]
                if mhwp_record.empty:
                    print(f"Error: MHW '{mhwp_username}' does not exist or is not a valid MHW.")
                    return False
            except FileNotFoundError:
                print("Error: user_data.csv file not found.")
                return False

            # Check MHW schedule in mhwp_schedule.csv
            try:
                schedule = pd.read_csv(schedule_file)
                mhwp_schedule = schedule[(schedule['mhwp_username'] == mhwp_username) & (schedule['date'] == date)]
                
                if mhwp_schedule.empty:
                    print(f"No schedule found for MHW '{mhwp_username}' on {date}.")
                    return False

                # Create a copy of the subset to avoid SettingWithCopyWarning
                mhwp_schedule = mhwp_schedule.copy()
                mhwp_schedule['start_time'] = pd.to_datetime(mhwp_schedule['start_time'], format='%H:%M')
                mhwp_schedule['end_time'] = pd.to_datetime(mhwp_schedule['end_time'], format='%H:%M')
                input_start_time = pd.to_datetime(start_time, format='%H:%M')
                input_end_time = pd.to_datetime(end_time, format='%H:%M')

                # Ensure booked time is within MHW's schedule
                within_schedule = mhwp_schedule[
                    (mhwp_schedule['start_time'] <= input_start_time) & (mhwp_schedule['end_time'] >= input_end_time)
                ]
                if within_schedule.empty:
                    print("The selected time slot is outside the MHW's scheduled hours. Please choose another.")
                    return False
            except FileNotFoundError:
                print("Error: mhwp_schedule.csv file not found.")
                return False

            # Check for conflicting appointments
            try:
                appointments = pd.read_csv(appointment_file)
                appointments['start_time'] = pd.to_datetime(appointments['start_time'], format='%H:%M')
                appointments['end_time'] = pd.to_datetime(appointments['end_time'], format='%H:%M')
            except FileNotFoundError:
                # If no appointments file exists, create an empty DataFrame
                appointments = pd.DataFrame(columns=['mhwp_username', 'date', 'start_time', 'end_time', 'status'])

            # Check for overlapping time slots in appointments
            overlapping_appointment = appointments[
                (appointments['mhwp_username'] == mhwp_username) &
                (appointments['date'] == date) &
                (
                    ((appointments['start_time'] <= input_start_time) & (appointments['end_time'] > input_start_time)) |
                    ((appointments['start_time'] < input_end_time) & (appointments['end_time'] >= input_end_time))
                )
            ]
            if not overlapping_appointment.empty:
                print("The selected time slot overlaps with an existing appointment. Please choose another.")
                return False

            # Record the appointment in appointments.csv
            appointment = {
                "patient_username": self.username,
                "mhwp_username": mhwp_username,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "status": "pending"
            }
            appointment_df = pd.DataFrame([appointment])
            try:
                appointment_df.to_csv(appointment_file, mode='a', header=not pd.read_csv(appointment_file).shape[0], index=False)
            except FileNotFoundError:
                # If the file does not exist, create it
                appointment_df.to_csv(appointment_file, mode='w', header=True, index=False)

            print("Appointment booked successfully!")
            return True

        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def view_appointments(self, appointment_file):
        """
        Allow an admin to view all appointments for patients and MHWs.
        """
        if self.role != "admin":
            print("Only admins can view all appointments.")
            return False

        try:
            appointments = pd.read_csv(appointment_file)
            if appointments.empty:
                print("No appointments found.")
            else:
                print(appointments[['patient_username', 'mhwp_username', 'date', 'start_time', 'end_time', 'status']])
        except FileNotFoundError:
            print("Appointment file not found.")
        except Exception as e:
            print(f"Unexpected error: {e}")



    def manage_appointments(self, appointment_file, action, patient_username=None, date=None, start_time=None):
        """
        Manage appointments (confirm, cancel, or view) for MHWs.
        """
        if self.role != "mhwp":
            print("Only MHWs can manage appointments.")
            return False

        try:
            appointments = pd.read_csv(appointment_file)

            if action == "view":
                # View all appointments related to the MHW
                user_appointments = appointments[appointments['mhwp_username'] == self.username]
                if user_appointments.empty:
                    print("No appointments found.")
                else:
                    print(user_appointments[['patient_username', 'date', 'start_time', 'end_time', 'status']])

            elif action in ["confirm", "cancel"]:
                # Confirm or cancel a specific appointment
                appointment_filter = (appointments['patient_username'] == patient_username) & \
                                     (appointments['date'] == date) & \
                                     (appointments['start_time'] == start_time) & \
                                     (appointments['mhwp_username'] == self.username)
                if not appointment_filter.any():
                    print("Appointment not found.")
                    return False

                new_status = "confirmed" if action == "confirm" else "cancelled"
                appointments.loc[appointment_filter, 'status'] = new_status
                appointments.to_csv(appointment_file, index=False)
                print(f"Appointment has been {new_status}.")
                return True

        except FileNotFoundError:
            print("Appointment file not found.")
            return False
        except Exception as e:
            print(f"Error while managing appointments: {e}")
            return False

    def display_info(self):
        """Display user information."""
        print(f"Username: {self.username}, Role: {self.role}")
        
    def admin_delete_user(self, username):
        """Admin method to delete a user and their associated patient record if applicable."""
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
            
            # Prepare the DataFrame
            try:
                df = pd.read_csv(patient_data_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=[
                    "username", "assigned_mhwp", "account_status",
                    "registration_date", "email", "emergency_email", "Record"
                ])

            # Create new patient record WITHOUT password
            new_patient = pd.DataFrame({
                "username": [self.username],
                "assigned_mhwp": [""],
                "account_status": ["active"],  
                "registration_date": [datetime.now().strftime("%Y-%m-%d")],
                "email": [self.email if self.email else ""],
                "emergency_email": [self.emergency_email if self.emergency_email else ""],
                "Record": [""]
            })

            df = pd.concat([df, new_patient], ignore_index=True)
            df.to_csv(patient_data_path, index=False, na_rep='')
            print("Patient record initialized successfully.")
            return True

        except Exception as e:
            print(f"Error creating patient record: {str(e)}")
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