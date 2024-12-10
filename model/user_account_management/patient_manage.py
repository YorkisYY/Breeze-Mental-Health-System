import pandas as pd
from datetime import datetime
from config import PATIENTS_DATA_PATH

class PatientManage:
    """
    A class to handle patient record management operations including initialization,
    status updates, and MHWP assignments.
    
    This class provides functionality for:
    - Creating new patient records
    - Checking existing patient records
    - Updating patient account status (freezing/unfreezing)
    - Managing MHWP assignments to patients
    """

    def check_patient_record_exists(self, patient_data_path=PATIENTS_DATA_PATH):
        """
        Check if a patient record already exists in the system.

        Args:
            patient_data_path (str): Path to the patient data CSV file.
                                   Defaults to PATIENTS_DATA_PATH from config.

        Returns:
            bool: True if patient record exists, False otherwise.

        Note:
            Uses the patient's username to check existence in the CSV file.
        """
        try:
            df = pd.read_csv(patient_data_path)
            return self.username in df['username'].values
        except FileNotFoundError:
            return False
            
    def initialize_patient_record(self, patient_data_path=PATIENTS_DATA_PATH):
        """
        Initialize a new patient record with complete user information.

        Args:
            patient_data_path (str): Path to the patient data CSV file.
                                   Defaults to PATIENTS_DATA_PATH from config.

        Returns:
            bool: True if initialization successful, False otherwise.

        Process:
        1. Verifies user role is 'patient'
        2. Checks if record already exists
        3. Creates or loads patient data file
        4. Adds new patient information
        5. Saves updated records

        Fields initialized:
        - username
        - assigned_mhwp (empty initially)
        - account_status (active by default)
        - registration_date (current date)
        - email
        - emergency_email
        - symptoms
        """
        # Verify user role
        if self.role != "patient":
            print("Only patients can have patient records.")
            return False

        try:
            # Check for existing record
            if self.check_patient_record_exists():
                print("Patient record already exists.")
                return False
            
            # Load or create patient data file
            try:
                df = pd.read_csv(patient_data_path)
            except FileNotFoundError:
                # Initialize new DataFrame with required columns
                df = pd.DataFrame(columns=[
                    "username", "assigned_mhwp", "account_status",
                    "registration_date", "email", "emergency_email", "symptoms"
                ])

            # Create new patient record
            new_patient = pd.DataFrame({
                "username": [self.username],
                "assigned_mhwp": [""],  # Empty initially
                "account_status": ["active"],  # Default status
                "registration_date": [datetime.now().strftime("%Y-%m-%d")],
                "email": [self.email if self.email else ""],
                "emergency_email": [self.emergency_email if self.emergency_email else ""],
                "symptoms": [self.symptoms if self.symptoms else ""]
            })

            # Add new record and save
            df = pd.concat([df, new_patient], ignore_index=True)
            df.to_csv(patient_data_path, index=False, na_rep='')
            print("Patient record initialized successfully.")
            return True

        except Exception as e:
            print(f"Error creating patient record: {str(e)}")
            return False
            
    def update_patient_status(self, patient_username, status, patient_data_path=PATIENTS_DATA_PATH):
        """
        Update patient account status (freeze/unfreeze account).
        Admin-only function.

        Args:
            patient_username (str): Username of the patient to update
            status (str): New status - 'yes' for frozen, 'no' for active
            patient_data_path (str): Path to patient data file

        Returns:
            bool: True if update successful, False otherwise

        Notes:
            - Only admins can perform this operation
            - Status must be either 'yes' (frozen) or 'no' (active)
        """
        # Verify admin privileges
        if self.role != "admin":
            print("Only admin can update patient status.")
            return False
            
        # Validate status input
        if status not in ['yes', 'no']:
            print("Invalid status. Use 'yes' for frozen or 'no' for active.")
            return False
            
        try:
            # Load and update patient data
            df = pd.read_csv(patient_data_path)
            if patient_username not in df['username'].values:
                print("Patient record not found.")
                return False
                
            # Update status and save
            df.loc[df['username'] == patient_username, 'account_status'] = status
            df.to_csv(patient_data_path, index=False)
            status_text = "frozen" if status == "yes" else "activated"
            print(f"Patient account {patient_username} has been {status_text}")
            return True
            
        except Exception as e:
            print(f"Error updating patient status: {str(e)}")
            return False

    def update_patient_mhwp(self, patient_username, mhwp_username, patient_data_path=PATIENTS_DATA_PATH):
        """
        Assign or update MHWP for a patient.
        Admin-only function.

        Args:
            patient_username (str): Username of the patient
            mhwp_username (str): Username of the MHWP to assign
            patient_data_path (str): Path to patient data file

        Returns:
            bool: True if update successful, False otherwise

        Notes:
            - Only admins can perform this operation
            - Updates existing MHWP assignment if one exists
        """
        # Verify admin privileges
        if self.role != "admin":
            print("Only admin can assign MHWPs to patients.")
            return False
            
        try:
            # Load and update patient data
            df = pd.read_csv(patient_data_path)
            if patient_username not in df['username'].values:
                print("Patient record not found.")
                return False
                
            # Update MHWP assignment and save
            df.loc[df['username'] == patient_username, 'assigned_mhwp'] = mhwp_username
            df.to_csv(patient_data_path, index=False)
            print(f"MHWP {mhwp_username} assigned to patient {patient_username}")
            return True
            
        except Exception as e:
            print(f"Error updating patient's MHWP: {str(e)}")
            return False