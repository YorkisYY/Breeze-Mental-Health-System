from services.mood_tracking import MoodEntry
from services.meditation import handle_search_meditation
from services.journaling import enter_journaling
from services.patient_records import view_my_records
from services.questionnaire import submit_questionnaire

def handle_health_wellbeing(user):
    """
    Handle the Health & Wellbeing menu options for patients
    """
    while True:
        print("\nHealth & Wellbeing:")
        print("1. View Medical Records")
        print("2. Submit a Mood Questionnaire")
        print("3. Track Mood")
        print("4. Enter a Journaling")
        print("5. Explore Meditation Resources")
        print("6. Back to Main Menu")

        wellbeing_choice = input("Select an option (1-6): ").strip()

        if wellbeing_choice == '1':
            view_my_records(user.username)
        elif wellbeing_choice == '2':
            submit_questionnaire(user.username)      
        elif wellbeing_choice == '3':
            handle_mood_tracking(user)
        elif wellbeing_choice == '4':
            enter_journaling(user.username)  
        elif wellbeing_choice == '5':
            handle_search_meditation()  
        elif wellbeing_choice == '6':
            break  
        else:
            print("Invalid choice, please try again.")

def handle_mood_tracking(user):
    """
    Handle mood tracking functionality for patients
    """
    print("\nMood Tracking")
    print("How are you feeling today?")
    print("1. Green - Very Good (Feeling great, energetic, positive)")
    print("2. Blue - Good (Calm, content, peaceful)")
    print("3. Yellow - Neutral (OK, balanced)")
    print("4. Orange - Not Great (Worried, uneasy)")
    print("5. Red - Poor (Distressed, anxious, depressed)")
    
    color_choice = input("Select your mood (1-5): ").strip()
    if color_choice in ["1", "2", "3", "4", "5"]:
        comments = input("Would you like to add any comments about your mood? ").strip()
        mood_entry = MoodEntry(user.username, color_choice, comments)
        mood_entry.save_mood_entry()
        
        display_mood_history(user.username)
    else:
        print("Invalid mood selection.")

def display_mood_history(username):
    """
    Display recent mood history for a patient
    """
    print("\nYour recent mood history:")
    history = MoodEntry.get_user_mood_history(username)
    if not history.empty:
        print(history[['timestamp', 'color_code', 'comments']].head())