import pandas as pd
import random
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import *

MAJORS = [
    "Emotional Management",
    "Behavioral Therapy",
    "Severe Disorders",
    "General Wellbeing"
]

CONDITIONS = [
    "Anxiety", "Depression", "PTSD", "Bipolar Disorder",
    "OCD", "ADHD", "Eating Disorder", "Substance Abuse",
    "Schizophrenia", "Borderline Personality Disorder",
    "Other/General Wellbeing"
]

def allocate_users(user_data_path=USER_DATA_PATH, 
                  mhwp_data_path=MHWP_DATA_PATH,
                  patient_data_path=PATIENTS_DATA_PATH):
    """Allocate users from user_data.csv to role-specific files with random attributes"""
    
    # Read user data
    users_df = pd.read_csv(user_data_path)
    
    # Initialize MHWP dataframe
    mhwp_df = pd.DataFrame(columns=[
        "username", "assigned_patients", "account_status",
        "registration_date", "email", "emergency_email", "major"
    ])
    
    # Initialize Patient dataframe
    patient_df = pd.DataFrame(columns=[
        "username", "assigned_mhwp", "account_status",
        "registration_date", "email", "emergency_email", "symptoms"
    ])
    
    # Process each user
    for _, user in users_df.iterrows():
        if user['role'] == 'mhwp':
            new_mhwp = {
                "username": user['username'],
                "assigned_patients": "",
                "account_status": "active",
                "registration_date": datetime.now().strftime("%Y-%m-%d"),
                "email": user['email'],
                "emergency_email": user['emergency_email'],
                "major": random.choice(MAJORS)
            }
            mhwp_df = pd.concat([mhwp_df, pd.DataFrame([new_mhwp])], ignore_index=True)
            
        elif user['role'] == 'patient':
            # Random number of conditions (1-3)
            num_conditions = random.randint(1, 3)
            selected_conditions = random.sample(CONDITIONS, num_conditions)
            
            new_patient = {
                "username": user['username'],
                "assigned_mhwp": "",
                "account_status": "active",
                "registration_date": datetime.now().strftime("%Y-%m-%d"),
                "email": user['email'],
                "emergency_email": user['emergency_email'],
                "symptoms": ",".join(selected_conditions)
            }
            patient_df = pd.concat([patient_df, pd.DataFrame([new_patient])], ignore_index=True)
    
    # Save to files
    mhwp_df.to_csv(mhwp_data_path, index=False)
    patient_df.to_csv(patient_data_path, index=False)
    
    print(f"Allocated {len(mhwp_df)} MHWPs and {len(patient_df)} patients")

allocate_users()