import pandas as pd
import hashlib
from datetime import datetime
from config import USER_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH
from .base import UserBase
from .user_data_manage import UserDataManage
from .user_update import UserUpdate
from .admin_manage import AdminManage
from .patient_manage import PatientManage
from .mhwp_manage import MhwpManage

class User(UserBase, UserDataManage, UserUpdate, PatientManage, MhwpManage, AdminManage):
    """
    User class that combines all functionality through inheritance
    """
    def __init__(self, username, password, role, email=None, emergency_email=None, symptoms=None, major=None):
        UserBase.__init__(self, username, password, role, email, emergency_email)
        self.symptoms = symptoms
        self.major = major
        
    def save_to_csv(self):
        """Save user to CSV and initialize role-specific records."""
        try:
            if not UserDataManage.save_to_csv(self):
                return False

            if self.role == "patient" and not self.check_patient_record_exists():
                self.initialize_patient_record()
            elif self.role == "mhwp" and not self.check_mhwp_record_exists():
                self.initialize_mhwp_record()

            return True
        except Exception as e:
            print(f"Error saving user data: {str(e)}")
            return False

    def load_from_csv(self):
        """Load user data and role-specific information."""
        try:
            if not UserDataManage.load_from_csv(self):
                return False

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
            elif self.role == "mhwp":
                try:
                    mhwp_df = pd.read_csv(MHWP_DATA_PATH)
                    mhwp_info = mhwp_df[mhwp_df['username'] == self.username]
                    if not mhwp_info.empty:
                        self.assigned_patients = mhwp_info.iloc[0]['assigned_patients']
                        self.account_status = mhwp_info.iloc[0]['account_status']
                        self.registration_date = mhwp_info.iloc[0]['registration_date']
                        self.major = mhwp_info.iloc[0]['major']
                except FileNotFoundError:
                    pass

            return True
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            return False