import hashlib
import pandas as pd
from config import USER_DATA_PATH
class UserBase:
    def __init__(self, username, password, role, email=None, emergency_email=None, symptoms=None, major=None):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
        self.email = email
        self.emergency_email = emergency_email
        self.appointments = []
        self.symptoms = symptoms
        self.major = major
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_if_exists(self):
        """Check if user exists in CSV."""
        try:
            df = pd.read_csv(USER_DATA_PATH)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False