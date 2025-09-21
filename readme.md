Breeze Mental Health Management System 🌞
A comprehensive mental health management system built in Python that facilitates communication and care coordination between patients and Mental Health Wellbeing Personnel (MHWP).
🌟 Features
For Patients

Account Management: Secure registration, login, and profile updates
Health & Wellbeing Tracking:

Mood tracking with color-coded system (Green/Blue/Yellow/Orange/Red)
Personal journaling entries
Mental health questionnaires with automated feedback


Appointment Management: Book, cancel, and view appointments with assigned MHWPs
Meditation Resources: Search and explore guided meditation content
Medical Records: View personal medical history and treatment records
Comment System: Provide feedback on appointments and care quality

For Mental Health Workers (MHWP)

Schedule Management: Set availability templates and modify schedules
Patient Management: View assigned patients and their records
Appointment Handling: Confirm, cancel, and manage patient appointments
Patient Records Access:

View mood tracking data with visualizations
Access patient journals and assessments
Add medical notes and treatment records


Dashboard: Comprehensive overview of patient status and trends
Email Notifications: Automated appointment confirmations and updates

For Administrators

User Management: Create, modify, and deactivate user accounts
Assignment System: Intelligently assign patients to MHWPs based on:

MHWP specializations (Emotional Management, Behavioral Therapy, Severe Disorders, General Wellbeing)
Patient symptoms and conditions
MHWP availability and workload


System Analytics: View comprehensive reports and statistics
Account Status Control: Enable/disable user accounts as needed

🏗️ System Architecture
Core Components

Model Layer: User management, patient/MHWP data handling, admin functions
Services Layer: Business logic for appointments, mood tracking, notifications
Utils Layer: Helper functions, email configuration, user interface utilities

Key Technologies

Python 3.x: Core programming language
Pandas: Data manipulation and CSV file handling
Matplotlib: Data visualization for mood trends
SMTP: Email notification system
Scikit-learn: Machine learning for mood prediction (TF-IDF + K-means clustering)

📁 Project Structure
breeze-mental-health/
├── main.py                 # Application entry point
├── config.py              # Configuration and file paths
├── model/                 # Data models and business logic
│   ├── admin.py
│   ├── patient.py
│   ├── mhwp.py
│   └── user_account_management/
├── services/              # Core services
│   ├── login.py
│   ├── registration.py
│   ├── mood_tracking.py
│   ├── appointment.py
│   └── dashboard.py
├── utils/                 # Utility functions
│   ├── notification.py
│   ├── display_banner.py
│   └── email_config.ini
└── data/                  # CSV data files
    ├── user_data.csv
    ├── patients.csv
    ├── mhwp.csv
    └── appointments.csv
🚀 Installation & Setup
Prerequisites

Python 3.8 or higher
pip package manager

Required Libraries
bashpip install pandas matplotlib tabulate
Configuration

Email Setup (Optional):

Edit utils/email_config.ini with your SMTP settings
Default configuration uses Gmail SMTP


Data Directory:

The system automatically creates necessary CSV files
Initial data structure is set up on first run



Running the Application
bashpython main.py
👥 User Roles & Access
Default Verification Codes

Admin Registration: 0000
MHWP Registration: 0000
Patient Registration: No code required

MHWP Specializations

Emotional Management: Anxiety, Depression, PTSD, Bipolar Disorder
Behavioral Therapy: OCD, ADHD, Eating Disorder, Substance Abuse
Severe Disorders: Schizophrenia, Borderline Personality Disorder
General Wellbeing: Other conditions and general support

📊 Key Features Deep Dive
Intelligent Assignment System
The system automatically assigns patients to MHWPs based on:

Symptom Matching: Patients are matched with MHWPs whose specialization covers their conditions
Workload Balancing: Distribution considers current patient loads
Schedule Availability: Only MHWPs with set schedules receive assignments

Mood Tracking & Analytics

5-Point Color System: Visual mood representation
Trend Analysis: Matplotlib visualizations show mood patterns over time
Predictive Analytics: Machine learning model predicts mood based on journal entries

Appointment Management

Real-time Scheduling: Dynamic schedule updates with conflict prevention
Status Tracking: Pending → Confirmed → Completed workflow
Automated Notifications: Email alerts for all appointment changes
