import pandas as pd
from datetime import datetime, timedelta
from config import MENTAL_ASSESSMENTS_PATH


# Mental health questionnaire questions and scoring standards
QUESTIONS = {
    "Depression": [
        "In the past two weeks, have you felt down, depressed, or hopeless?",
        "Have you had little interest or pleasure in doing things?",
        "Have you felt tired or had little energy?"
    ],
    "Anxiety": [
        "In the past two weeks, have you felt nervous, anxious, or on edge?",
        "Have you found it hard to stop or control worrying?",
        "Have you had trouble relaxing?"
    ],
    "Autism": [
        "Do you find it hard to understand social cues or body language?",
        "Do you often feel the need to stick to routines or have difficulty adapting to changes?",
        "Do you feel overwhelmed in social situations?"
    ]
}

STATUS_FEEDBACK = {
    "Depression": "Take a moment for yourself today. Seek out small joys and share them with someone you trust.",
    "Anxiety": "Remember to breathe deeply. It's okay to take things one step at a time.",
    "Autism": "You're unique and valued. Expressing yourself in your own way is perfectly okay."
}

def calculate_score(responses):
    """Calculate the score based on responses, where 1-5 corresponds to low to high intensity."""
    return sum(int(response) for response in responses)

def generate_feedback(status_list):
    """Generate positive feedback."""
    feedback = []
    for status in status_list:
        if status in STATUS_FEEDBACK:
            feedback.append(STATUS_FEEDBACK[status])
    return "\n".join(feedback)

def submit_questionnaire(patient_username, assignments_file="data/assignments.csv"):
    """
    Allow the patient to complete the questionnaire and store the results.
    Now reads from the assignment.csv file.
    """
    try:
        # Load the assignment data
        assignments = pd.read_csv(assignments_file)

        # Filter assignments for the current patient
        patient_assignment = assignments[assignments["patient_username"] == patient_username]
        if patient_assignment.empty:
            print("Error: No MHWP found for this patient.")
            return

        # Retrieve the assigned MHWP username
        mhwp_username = patient_assignment.iloc[0]["mhwp_username"]
        print(f"Assigned MHWP for patient '{patient_username}': {mhwp_username}")
    except FileNotFoundError:
        print("Error: Assignments file not found.")
        return
    except Exception as e:
        print(f"Error: {e}")


    print("\nWelcome to the Mental Health Questionnaire!")
    print("For each question, answer with a number between 1 (Not at all) to 5 (Nearly every day).")

    results = {}
    for category, questions in QUESTIONS.items():
        print(f"\nCategory: {category}")
        responses = []
        for question in questions:
            while True:
                try:
                    response = int(input(f"{question} (1-5): ").strip())
                    if 1 <= response <= 5:
                        responses.append(response)
                        break
                    else:
                        print("Please enter a number between 1 and 5.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        results[category] = calculate_score(responses)

    status = [category for category, score in results.items() if score >= 10]
    feedback = generate_feedback(status)
    if not feedback:  # 如果反馈为空，则生成默认反馈
        feedback = "Thank you for completing the questionnaire. No potential issues have been detected at this time. Please continue to pay attention to your mental health and seek professional help if necessary."

    assessment_data = {
        "patient_username": patient_username,
        "mhwp_username": mhwp_username,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": sum(results.values()),
        "status": ", ".join(status) if status else "Normal"
    }
    try:
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_PATH)
        # Change: Replace append with pd.concat
        assessments_df = pd.concat([assessments_df, pd.DataFrame([assessment_data])], ignore_index=True)
    except FileNotFoundError:
        assessments_df = pd.DataFrame([assessment_data])

    assessments_df.to_csv(MENTAL_ASSESSMENTS_PATH, index=False)
    print("\nThank you for completing the questionnaire!")
    print(f"Your feedback:\n{feedback}")


def remind_to_complete_questionnaire(patient_username):
    """
    Remind the patient to complete the mental health questionnaire. If more than two weeks have passed, remind and guide them to complete it.
    """
    try:
        # Read the questionnaire records
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_PATH)
    except FileNotFoundError:
        # If the questionnaire file does not exist, create an empty file and directly remind
        assessments_df = pd.DataFrame(columns=["patient_username", "mhwp_username", "date", "score", "status"])
        assessments_df.to_csv(MENTAL_ASSESSMENTS_PATH, index=False)

    # Filter records for the current patient
    patient_records = assessments_df[assessments_df["patient_username"] == patient_username]

    if patient_records.empty:
        # If no records exist, directly remind
        print("You have not completed any questionnaires yet.")
        complete_now = input("Would you like to complete the questionnaire now? (yes/no): ").strip().lower()
        if complete_now == "yes":
            submit_questionnaire(patient_username)
        return

    # Get the date of the last completed questionnaire
    last_date_str = patient_records.iloc[-1]["date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    days_since_last = (datetime.now() - last_date).days

    if days_since_last >= 14:
        # If more than two weeks, remind and guide to complete the questionnaire
        print(f"It has been {days_since_last} days since you last completed a questionnaire.")
        complete_now = input("Would you like to complete the questionnaire now? (yes/no): ").strip().lower()
        if complete_now == "yes":
            submit_questionnaire(patient_username)
    else:
        # If within two weeks, skip the reminder
        print(f"You completed a questionnaire {days_since_last} days ago. No need to complete another now.")

