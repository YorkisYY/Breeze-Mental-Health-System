import os

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Global file paths
USER_DATA_PATH = os.path.join(DATA_DIR, 'user_data.csv')
MOOD_DATA_PATH = os.path.join(DATA_DIR, 'mood_data.csv')
PATIENTS_DATA_PATH = os.path.join(DATA_DIR, 'patients.csv')
MHWP_DATA_PATH = os.path.join(DATA_DIR, 'mhwp.csv')
APPOINTMENTS_DATA_PATH = os.path.join(DATA_DIR, 'appointments.csv')
SCHEDULE_DATA_PATH = os.path.join(DATA_DIR, 'mhwp_schedule.csv')
MHWP_SCHEDULE_TEMPLATE_PATH = os.path.join(DATA_DIR, 'mhwp_schedule_template.csv')
JOURNAL_ENTRIES_PATH = os.path.join(DATA_DIR,'patient_journaling.csv')
ASSIGNMENTS_DATA_PATH = os.path.join(DATA_DIR, 'assignments.csv')
MENTAL_ASSESSMENTS_PATH = os.path.join(DATA_DIR, 'mental_assessments.csv')
PATIENT_NOTES_PATH = os.path.join(DATA_DIR, 'patient_notes.csv')
MEDITATION_RESOURCES_PATH = os.path.join(DATA_DIR, 'meditation_resources.csv')
COMMENTS_PATH = os.path.join(DATA_DIR, 'comments.csv')
# OTHER_DATA_PATH = os.path.join(DATA_DIR, '#place your csv file name here')
set_start_hour = 9 # start hour of the day's schedule
set_end_hour = 16 # end hour of the day's schedule