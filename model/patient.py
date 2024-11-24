import os
from services.mood_tracking import MoodEntry

def handle_patient_menu(user, file_path):
    while True:
        print("\nPatient Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. View Medical Records")
        print("4. Book Appointment")
        print("5. Delete Account")
        print("6. Track Mood")
        print("7. Logout")
        
        patient_choice = input("Select an option (1-7): ")
        if patient_choice == '1':
            new_username = input("Enter new username: ").strip()
            user.update_info(file_path, new_username=new_username)
        elif patient_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(file_path, new_password)
        elif patient_choice == '3':
            print("Medical records feature coming soon...")
        elif patient_choice == '4':
            print("Appointment booking feature coming soon...")
        elif patient_choice == '5':
            confirm = input("Confirm delete account? (yes/no): ")
            if confirm.lower() == "yes":
                user.delete_from_csv(file_path)
                print("Account deleted successfully.")
                break
        elif patient_choice == '6':
            handle_mood_tracking(user)
        elif patient_choice == '7':
            print("Logging out.")
            break
        else:
            print("Invalid choice, please try again.")

def handle_mood_tracking(user):
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
        DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
        MOOD_DATA_PATH = os.path.join(DATA_DIR, 'mood_data.csv')
        mood_entry.save_mood_entry(MOOD_DATA_PATH)
        
        display_mood_history(user.username)
    else:
        print("Invalid mood selection.")

def display_mood_history(username):
    print("\nYour recent mood history:")
    history = MoodEntry.get_user_mood_history("mood_data.csv", username)
    if not history.empty:
        print(history[['timestamp', 'color_code', 'comments']].head())
