import pandas as pd
import hashlib

class User:
    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = self.hash_password(password)  # Encrypt the password
        self.role = role

    def hash_password(self, password):
        # Simple password hashing method (suggest using a more secure encryption)
        return hashlib.sha256(password.encode()).hexdigest()

    def save_to_csv(self, file_path):
        # Save user information to a CSV file
        user_data = {
            "username": [self.username],
            "password": [self.password],
            "role": [self.role]
        }
        df = pd.DataFrame(user_data)
        df.to_csv(file_path, mode='a', index=False, header=False)

    def load_from_csv(self, file_path):
        # Load user information from a CSV file to check if the user exists
        try:
            df = pd.read_csv(file_path)
            user_info = df[df['username'] == self.username]
            if not user_info.empty:
                self.password = user_info.iloc[0]['password']
                self.role = user_info.iloc[0]['role']
                return True
            else:
                return False
        except FileNotFoundError:
            print("User data file not found.")
            return False

    def update_info(self, new_username=None, new_password=None):
        # Update user information
        if new_username:
            self.username = new_username
        if new_password:
            self.password = self.hash_password(new_password)

    def delete_from_csv(self, file_path):
        # Delete user information from the CSV file
        df = pd.read_csv(file_path)
        df = df[df['username'] != self.username]
        df.to_csv(file_path, index=False)

    def display_info(self):
        # Display user information (for debugging purposes)
        print(f"Username: {self.username}, Role: {self.role}")
