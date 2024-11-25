import pandas as pd
import hashlib
from config import USER_DATA_PATH

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.medical_records = []
        self.appointments = []

    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def save_to_csv(self):
        """Save user information to CSV, ensuring no duplicate usernames."""
        if self.check_if_exists():
            print("Username has been used. Please choose a different one.")
            return False
        user_data = {"username": [self.username], "password": [self.password], "role": [self.role]}
        df = pd.DataFrame(user_data)
        df.to_csv(USER_DATA_PATH, mode='a', index=False, header=False)
        return True

    def load_from_csv(self):
        """Load user info from CSV to check if user exists."""
        try:
            df = pd.read_csv(USER_DATA_PATH)
            user_info = df[df['username'] == self.username]
            if not user_info.empty:
                self.password = user_info.iloc[0]['password']
                self.role = user_info.iloc[0]['role']
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

    def update_info(self, new_username=None, new_password=None):
        """Update user information if changes are made."""
        if not self.load_from_csv():
            print("User does not exist.")
            return False

        try:
            df = pd.read_csv(USER_DATA_PATH)

            if new_username == self.username:
                print("New username same as current. No changes made.")
                return False

            hashed_new_password = self.hash_password(new_password) if new_password else None
            if hashed_new_password == self.password:
                print("New password same as current. No changes made.")
                return False

            if new_username:
                if new_username in df['username'].values:
                    print("Username already in use.")
                    return False
                df.loc[df['username'] == self.username, 'username'] = new_username
                self.username = new_username

            if new_password:
                df.loc[df['username'] == self.username, 'password'] = hashed_new_password
                self.password = hashed_new_password

            df.to_csv(USER_DATA_PATH, index=False)
            print("User information updated successfully.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def update_password(self, new_password):
        """Update user password."""
        if not self.load_from_csv():
            print("User does not exist.")
            return False

        try:
            df = pd.read_csv(USER_DATA_PATH)

            hashed_new_password = self.hash_password(new_password)
            if hashed_new_password == self.password:
                print("New password same as current. No changes made.")
                return False

            df.loc[df['username'] == self.username, 'password'] = hashed_new_password
            self.password = hashed_new_password

            df.to_csv(USER_DATA_PATH, index=False)
            print("User password updated successfully.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def delete_from_csv(self):
        """Delete user from CSV file."""
        try:
            df = pd.read_csv(USER_DATA_PATH)
            df = df[df['username'] != self.username]
            df.to_csv(USER_DATA_PATH, index=False)
            print("User deleted successfully.")
        except FileNotFoundError:
            print("User data file not found.")

    def admin_update_user(self, target_username, new_username=None, new_password=None):
        """Admin method to update other users."""
        if self.role != "admin":
            print("Only admin users can update others.")
            return False

        try:
            df = pd.read_csv(USER_DATA_PATH)
            if target_username not in df['username'].values:
                print("Target user does not exist.")
                return False

            if new_username == target_username:
                print("New username same as current.")
                return False

            target_user = df[df['username'] == target_username].iloc[0]
            hashed_new_password = self.hash_password(new_password) if new_password else None
            
            if hashed_new_password and hashed_new_password == target_user['password']:
                print("New password same as current.")
                return False

            if new_username:
                if new_username in df['username'].values:
                    print("Username already in use.")
                    return False
                df.loc[df['username'] == target_username, 'username'] = new_username

            if new_password:
                df.loc[df['username'] == target_username, 'password'] = hashed_new_password

            df.to_csv(USER_DATA_PATH, index=False)
            print("User updated successfully by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def admin_delete_user(self, target_username):
        """Admin method to delete other users."""
        if self.role != "admin":
            print("Only admin users can delete others.")
            return False

        try:
            df = pd.read_csv(USER_DATA_PATH)
            if target_username not in df['username'].values:
                print("Target user does not exist.")
                return False

            df = df[df['username'] != target_username]
            df.to_csv(USER_DATA_PATH, index=False)
            print(f"User '{target_username}' deleted by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def add_medical_record(self, record):
        """Add medical record for patient"""
        if self.role not in ["doctor", "mhw"]:
            print("Only medical staff can add records.")
            return False
        self.medical_records.append(record)
        return True

    def view_medical_records(self, patient_username):
        """View patient medical records"""
        if self.role not in ["admin", "doctor", "mhw"]:
            print("Unauthorized to view records.") 
            return None
        # Implementation for viewing records
        pass

    def book_appointment(self, mhwp_username, date, start_time, end_time, schedule_file, appointment_file):
        """
        Allow a patient to book an appointment with an MHW.
        Checks for availability and records the booking.
        """
        if self.role != "patient":
            print("Only patients can book appointments.")
            return False

        try:
            # Read MHW schedule
            schedule = pd.read_csv(schedule_file)
            mhwp_schedule = schedule[(schedule['mhwp_username'] == mhwp_username) &
                                     (schedule['date'] == date)]

            # Check if the selected time slot exists in MHW's schedule
            available_slot = mhwp_schedule[
                (mhwp_schedule['start_time'] == start_time) & (mhwp_schedule['end_time'] == end_time)
            ]
            if available_slot.empty:
                print("The selected time slot is not available in the MHW's schedule. Please choose another.")
                return False

            # Check if the selected time slot is already booked
            appointments = pd.read_csv(appointment_file)
            booked_slot = appointments[
                (appointments['mhwp_username'] == mhwp_username) &
                (appointments['date'] == date) &
                (appointments['start_time'] == start_time)
            ]
            if not booked_slot.empty:
                print("The selected time slot is already booked. Please choose another.")
                return False

            # Append the appointment to the appointments.csv file
            appointment = {
                "patient_username": self.username,
                "mhwp_username": mhwp_username,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "status": "pending"
            }
            appointment_df = pd.DataFrame([appointment])
            appointment_df.to_csv(appointment_file, mode='a', header=not pd.read_csv(appointment_file).shape[0], index=False)
            print("Appointment booked successfully!")
            return True

        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False
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