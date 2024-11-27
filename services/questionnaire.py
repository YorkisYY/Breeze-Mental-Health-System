import pandas as pd
from datetime import datetime, timedelta

MENTAL_ASSESSMENTS_FILE = "data/mental_assessments.csv"

# 心理问卷问题及评分标准
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
    """根据回答计算分数，1-5 分对应低到高强度"""
    return sum(int(response) for response in responses)

def generate_feedback(status_list):
    """生成正向反馈"""
    feedback = []
    for status in status_list:
        if status in STATUS_FEEDBACK:
            feedback.append(STATUS_FEEDBACK[status])
    return "\n".join(feedback)

def submit_questionnaire(patient_username, appointments_file="data/appointments.csv"):
    """让患者完成问卷并存储结果"""
    # 获取患者对应的 MHWP
    try:
        appointments = pd.read_csv(appointments_file)
        patient_appointment = appointments[appointments["patient_username"] == patient_username]
        if patient_appointment.empty:
            print("Error: No MHWP found for this patient.")
            return
        mhwp_username = patient_appointment.iloc[0]["mhwp_username"]
    except FileNotFoundError:
        print("Error: Appointments file not found.")
        return

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

    # 计算心理状态
    status = [category for category, score in results.items() if score >= 10]  # 简单假设 ≥10 为异常
    feedback = generate_feedback(status)

    # 保存问卷结果
    assessment_data = {
        "patient_username": patient_username,
        "mhwp_username": mhwp_username,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": sum(results.values()),
        "status": ", ".join(status) if status else "Normal"
    }
    try:
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_FILE)
        assessments_df = assessments_df.append(assessment_data, ignore_index=True)
    except FileNotFoundError:
        assessments_df = pd.DataFrame([assessment_data])

    assessments_df.to_csv(MENTAL_ASSESSMENTS_FILE, index=False)
    print("\nThank you for completing the questionnaire!")
    print(f"Your feedback:\n{feedback}")
    

def remind_to_complete_questionnaire(patient_username):
    """
    提醒患者完成心理问卷。如果超过两周未完成，则提醒并引导完成问卷。
    """
    try:
        # 读取问卷记录
        assessments_df = pd.read_csv(MENTAL_ASSESSMENTS_FILE)
    except FileNotFoundError:
        # 如果问卷文件不存在，创建空文件并直接提醒
        assessments_df = pd.DataFrame(columns=["patient_username", "mhwp_username", "date", "score", "status"])
        assessments_df.to_csv(MENTAL_ASSESSMENTS_FILE, index=False)

    # 筛选当前患者的记录
    patient_records = assessments_df[assessments_df["patient_username"] == patient_username]

    if patient_records.empty:
        # 如果没有记录，直接提醒
        print("You have not completed any questionnaires yet.")
        complete_now = input("Would you like to complete the questionnaire now? (yes/no): ").strip().lower()
        if complete_now == "yes":
            submit_questionnaire(patient_username)
        return

    # 获取最后一次完成问卷的日期
    last_date_str = patient_records.iloc[-1]["date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    days_since_last = (datetime.now() - last_date).days

    if days_since_last >= 14:
        # 如果超过两周，提醒并引导完成问卷
        print(f"It has been {days_since_last} days since you last completed a questionnaire.")
        complete_now = input("Would you like to complete the questionnaire now? (yes/no): ").strip().lower()
        if complete_now == "yes":
            submit_questionnaire(patient_username)
    else:
        # 如果在两周内，跳过提醒
        print(f"You completed a questionnaire {days_since_last} days ago. No need to complete another now.")
