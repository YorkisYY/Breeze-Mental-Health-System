import pandas as pd
import hashlib

class User:
    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role

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
            else:
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

            # Check if new values are the same as the current ones
            if new_username == self.username:
                print("The new username is the same as the current one. No changes made.")
                return False

            hashed_new_password = self.hash_password(new_password) if new_password else None
            if hashed_new_password == self.password:
                print("The new password is the same as the current one. No changes made.")
                return False

            # Update user info if checks pass
            if new_username:
                if new_username in df['username'].values:
                    print("Username already in use, please choose another.")
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

    def delete_from_csv(self, file_path):
        """Delete user information from the CSV file."""
        try:
            df = pd.read_csv(file_path)
            df = df[df['username'] != self.username]
            df.to_csv(file_path, index=False)
            print("User deleted successfully.")
        except FileNotFoundError:
            print("User data file not found.")

    def admin_update_user(self, file_path, target_username, new_username=None, new_password=None):
        """Admin-specific method to update another user's info."""
        if self.role != "admin":
            print("Only admin users can update other users.")
            return False

        try:
            df = pd.read_csv(file_path)

            # Check if target user exists
            if target_username not in df['username'].values:
                print("The target user does not exist.")
                return False

            # Check if new values are the same as the current ones
            if new_username == target_username:
                print("The new username is the same as the current one. No changes made.")
                return False

            # Hash and check password
            target_user_info = df[df['username'] == target_username].iloc[0]
            hashed_new_password = self.hash_password(new_password) if new_password else None
            if hashed_new_password == target_user_info['password']:
                print("The new password is the same as the current one. No changes made.")
                return False

            # Update user info if checks pass
            if new_username:
                if new_username in df['username'].values:
                    print("Username already in use, please choose another.")
                    return False
                df.loc[df['username'] == target_username, 'username'] = new_username

            if new_password:
                df.loc[df['username'] == target_username, 'password'] = hashed_new_password

            df.to_csv(file_path, index=False)
            print("User information updated successfully by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def admin_delete_user(self, file_path, target_username):
        """Admin-specific method to delete another user's info."""
        if self.role != "admin":
            print("Only admin users can delete other users.")
            return False

        try:
            df = pd.read_csv(file_path)

            # Check if target user exists
            if target_username not in df['username'].values:
                print("The target user does not exist.")
                return False

            # Delete user info
            df = df[df['username'] != target_username]
            df.to_csv(file_path, index=False)
            print(f"User '{target_username}' deleted successfully by admin.")
            return True

        except FileNotFoundError:
            print("User data file not found.")
            return False

    def display_info(self):
        """Display user information (for debugging purposes)."""
        print(f"Username: {self.username}, Role: {self.role}")
