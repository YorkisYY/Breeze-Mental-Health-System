import pandas as pd
import hashlib

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

    def save_to_csv(self, file_path):
        """Save user information to CSV, ensuring no duplicate usernames."""
        if self.check_if_exists(file_path):
            print("Username has been used. Please choose a different one.")
            return False
        user_data = {"username": [self.username], "password": [self.password], "role": [self.role]}
        df = pd.DataFrame(user_data)
        df.to_csv(file_path, mode='a', index=False, header=False)
        return True

    def load_from_csv(self, file_path):
        """Load user info from CSV to check if user exists."""
        try:
            df = pd.read_csv(file_path)
            user_info = df[df['username'] == self.username]
            if not user_info.empty:
                self.password = user_info.iloc[0]['password']
                self.role = user_info.iloc[0]['role']
                return True
            return False
        except FileNotFoundError:
            print("User data file not found.")
            return False

    def check_if_exists(self, file_path):
        """Check if user exists in CSV."""
        try:
            df = pd.read_csv(file_path)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False

    def update_info(self, file_path, new_username=None, new_password=None):
        """Update user information if changes are made."""
        if not self.load_from_csv(file_path):
            print("User does not exist.")
            return False

        try:
            df = pd.read_csv(file_path)

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

            df.to_csv(file_path, index=False)
            print("User information updated successfully.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def update_password(self, file_path, new_password):
        """Update user password."""
        if not self.load_from_csv(file_path):
            print("User does not exist.")
            return False

        try:
            df = pd.read_csv(file_path)

            hashed_new_password = self.hash_password(new_password)
            if hashed_new_password == self.password:
                print("New password same as current. No changes made.")
                return False

            df.loc[df['username'] == self.username, 'password'] = hashed_new_password
            self.password = hashed_new_password

            df.to_csv(file_path, index=False)
            print("User password updated successfully.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def delete_from_csv(self, file_path):
        """Delete user from CSV file."""
        try:
            df = pd.read_csv(file_path)
            df = df[df['username'] != self.username]
            df.to_csv(file_path, index=False)
            print("User deleted successfully.")
        except FileNotFoundError:
            print("User data file not found.")

    def admin_update_user(self, file_path, target_username, new_username=None, new_password=None):
        """Admin method to update other users."""
        if self.role != "admin":
            print("Only admin users can update others.")
            return False

        try:
            df = pd.read_csv(file_path)
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

            df.to_csv(file_path, index=False)
            print("User updated successfully by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def admin_delete_user(self, file_path, target_username):
        """Admin method to delete other users."""
        if self.role != "admin":
            print("Only admin users can delete others.")
            return False

        try:
            df = pd.read_csv(file_path)
            if target_username not in df['username'].values:
                print("Target user does not exist.")
                return False

            df = df[df['username'] != target_username]
            df.to_csv(file_path, index=False)
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

    def book_appointment(self, doctor, date, time):
        """Book appointment for patient"""
        if self.role != "patient":
            print("Only patients can book appointments.")
            return False
        appointment = {
            "doctor": doctor,
            "date": date,
            "time": time,
            "status": "pending"
        }
        self.appointments.append(appointment)
        return True

    def manage_appointments(self, action, appointment_id):
        """Manage appointments for medical staff"""
        if self.role not in ["doctor", "mhw"]:
            print("Only medical staff can manage appointments.")
            return False
        # Implementation for managing appointments
        pass

    def display_info(self):
        """Display user information."""
        print(f"Username: {self.username}, Role: {self.role}")