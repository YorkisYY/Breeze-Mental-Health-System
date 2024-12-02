import pandas as pd
from datetime import datetime
from config import PATIENTS_DATA_PATH

class PatientManage:
    def check_patient_record_exists(self, patient_data_path=PATIENTS_DATA_PATH):
        """Check if the patient record already exists."""
        try:
            df = pd.read_csv(patient_data_path)
            return self.username in df['username'].values
        except FileNotFoundError:
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
            
    def update_patient_status(self, patient_username, status, patient_data_path=PATIENTS_DATA_PATH):
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

    def update_patient_mhwp(self, patient_username, mhwp_username, patient_data_path=PATIENTS_DATA_PATH):
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
