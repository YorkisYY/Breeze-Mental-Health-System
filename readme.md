# Breeze Mental Health Management System

A comprehensive mental health management system built in Python that facilitates communication and care coordination between patients and Mental Health Wellbeing Personnel (MHWP).

## Features

### For Patients

- **Account Management**: Secure registration, login, and profile updates
- **Health & Wellbeing Tracking**:
  - Mood tracking with color-coded system (Green/Blue/Yellow/Orange/Red)
  - Personal journaling entries
  - Mental health questionnaires with automated feedback
- **Appointment Management**: Book, cancel, and view appointments with assigned MHWPs
- **Meditation Resources**: Search and explore guided meditation content
- **Medical Records**: View personal medical history and treatment records
- **Comment System**: Provide feedback on appointments and care quality

### For Mental Health Workers (MHWP)

- **Schedule Management**: Set availability templates and modify schedules
- **Patient Management**: View assigned patients and their records
- **Appointment Handling**: Confirm, cancel, and manage patient appointments
- **Patient Records Access**: 
  - View mood tracking data with visualizations
  - Access patient journals and assessments
  - Add medical notes and treatment records
- **Dashboard**: Comprehensive overview of patient status and trends
- **Email Notifications**: Automated appointment confirmations and updates

### For Administrators

- **User Management**: Create, modify, and deactivate user accounts
- **Assignment System**: Intelligently assign patients to MHWPs based on:
  - MHWP specializations (Emotional Management, Behavioral Therapy, Severe Disorders, General Wellbeing)
  - Patient symptoms and conditions
  - MHWP availability and workload
- **System Analytics**: View comprehensive reports and statistics
- **Account Status Control**: Enable/disable user accounts as needed

## System Architecture

### Core Components

- **Model Layer**: User management, patient/MHWP data handling, admin functions
- **Services Layer**: Business logic for appointments, mood tracking, notifications  
- **Utils Layer**: Helper functions, email configuration, user interface utilities

### Key Technologies

- **Python 3.x**: Core programming language
- **Pandas**: Data manipulation and CSV file handling  
- **Matplotlib**: Data visualization for mood trends
- **SMTP**: Email notification system
- **Scikit-learn**: Machine learning for mood prediction (TF-IDF + K-means clustering)

## 📁 Project Structure

### Directory Structure

```
breeze-mental-health/
├── main.py                          # Application entry point
├── config.py                        # Configuration and file paths
├── model/                           # Data models and business logic
│   ├── admin.py                     # Admin management functions
│   ├── patient.py                   # Patient management functions
│   ├── mhwp.py                     # MHWP management functions
│   ├── user_account_management/     # User account handling
│   │   ├── __init__.py
│   │   ├── user.py                  # Main user class
│   │   ├── admin_manage.py         # Admin operations
│   │   ├── patient_manage.py       # Patient operations
│   │   └── mhwp_manage.py          # MHWP operations
│   ├── admin_management/           # Admin-specific functions
│   │   ├── __init__.py
│   │   ├── admin_assignment.py     # Assignment logic
│   │   └── admin_assign_patient.py # Assignment management
│   ├── mhwp_management/           # MHWP-specific functions
│   │   ├── __init__.py
│   │   ├── mhwp_schedule.py        # Schedule management
│   │   ├── mhwp_appointment.py     # Appointment handling
│   │   └── mhwp_availability.py   # Availability management
│   └── patient_management/        # Patient-specific functions
│       ├── __init__.py
│       ├── patient_account.py      # Account management
│       ├── health_wellbeing.py     # Health tracking
│       └── appointment.py          # Appointment booking
├── services/                      # Core services
│   ├── __init__.py
│   ├── login.py                    # Authentication service
│   ├── registration.py             # User registration
│   ├── mood_tracking.py           # Mood tracking functionality
│   ├── questionnaire.py           # Mental health assessments
│   ├── journaling.py              # Patient journaling
│   ├── meditation.py              # Meditation resources
│   ├── comment.py                 # Feedback system
│   ├── dashboard.py               # Analytics dashboard
│   ├── patient_records.py         # Medical records
│   ├── summary.py                 # System statistics
│   └── trainModal.py              # ML model training
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── notification.py            # Email notifications
│   ├── display_banner.py          # UI banner
│   ├── list_all_user.py          # User listing utilities
│   └── email_config.ini           # SMTP configuration
└── data/                          # CSV data files
    ├── user_data.csv              # User authentication data
    ├── patients.csv               # Patient records
    ├── mhwp.csv                   # MHWP records
    ├── appointments.csv           # Appointment data
    ├── assignments.csv            # Patient-MHWP assignments
    ├── mood_data.csv             # Mood tracking data
    ├── patient_journaling.csv    # Journal entries
    ├── mental_assessments.csv    # Assessment results
    ├── patient_notes.csv         # Medical notes
    ├── comments.csv              # Feedback data
    ├── meditation_resources.csv  # Meditation content
    ├── mhwp_schedule.csv         # MHWP schedules
    └── mhwp_schedule_template.csv # Schedule templates
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Required Libraries

```bash
pip install pandas matplotlib tabulate
```

### Configuration

1. **Email Setup** (Optional): 
   - Edit `utils/email_config.ini` with your SMTP settings
   - Default configuration uses Gmail SMTP

2. **Data Directory**:
   - The system automatically creates necessary CSV files
   - Initial data structure is set up on first run

### Running the Application

```bash
python main.py
```

## User Roles & Access

### Default Verification Codes
- **Admin Registration**: `0000`
- **MHWP Registration**: `0000`
- **Patient Registration**: No code required

### MHWP Specializations
1. **Emotional Management**: Anxiety, Depression, PTSD, Bipolar Disorder
2. **Behavioral Therapy**: OCD, ADHD, Eating Disorder, Substance Abuse
3. **Severe Disorders**: Schizophrenia, Borderline Personality Disorder
4. **General Wellbeing**: Other conditions and general support

## Key Features

### Intelligent Assignment System
The system automatically assigns patients to MHWPs based on:
- **Symptom Matching**: Patients are matched with MHWPs whose specialization covers their conditions
- **Workload Balancing**: Distribution considers current patient loads
- **Schedule Availability**: Only MHWPs with set schedules receive assignments

### Mood Tracking & Analytics
- **5-Point Color System**: Visual mood representation
- **Trend Analysis**: Matplotlib visualizations show mood patterns over time
- **Predictive Analytics**: Machine learning model predicts mood based on journal entries

### Appointment Management
- **Real-time Scheduling**: Dynamic schedule updates with conflict prevention
- **Status Tracking**: Pending → Confirmed → Completed workflow
- **Automated Notifications**: Email alerts for all appointment changes

## Security Features

- **Password Hashing**: SHA-256 encryption for all passwords
- **Role-based Access**: Strict permission controls for different user types
- **Account Status Management**: Ability to deactivate compromised accounts
- **Data Validation**: Input sanitization and format checking

