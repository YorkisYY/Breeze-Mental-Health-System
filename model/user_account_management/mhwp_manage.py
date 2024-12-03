import pandas as pd
from datetime import datetime
from config import MHWP_DATA_PATH

class MhwpManage:
    def check_mhwp_record_exists(self, mhwp_data_path=MHWP_DATA_PATH):
        """Check if the MHWP record already exists."""
        try:
            df = pd.read_csv(mhwp_data_path)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False
            
    def initialize_mhwp_record(self, mhwp_data_path=MHWP_DATA_PATH):
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

    def update_mhwp_major(self, mhwp_username, major, mhwp_data_path=MHWP_DATA_PATH):
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

    def update_mhwp_status(self, mhwp_username, status, mhwp_data_path=MHWP_DATA_PATH):
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