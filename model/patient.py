import os
from services.mood_tracking import MoodEntry

def handle_patient_menu(user):

    while True:
        print("\nPatient Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. View Medical Records")
        print("4. Book/Cancel Appointment")
        print("5. Delete Account")
        print("6. Track Mood")
        print("7. Logout")
        
        patient_choice = input("Select an option (1-7): ")
        if patient_choice == '1':
            new_username = input("Enter new username: ").strip()
            user.update_info(new_username=new_username)
        elif patient_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)
        elif patient_choice == '3':
            print("Medical records feature coming soon...")

        elif patient_choice == '4':  # Book/Cancel appointment
            print("\nBook/Cancel Appointment:")
            print("1. Book an appointment")
            print("2. Cancel an appointment")

            appointment_choice = input("Select an option (1/2): ").strip()

            if appointment_choice == "1":  # Book an appointment
                mhwp_username = input("Enter MHW username: ").strip()
                date = input("Enter appointment date (YYYY-MM-DD): ").strip()
                start_time = input("Enter start time (HH:MM): ").strip()
                end_time = input("Enter end time (HH:MM): ").strip()

                if user.book_appointment(mhwp_username, date, start_time, end_time, "data/mhwp_schedule.csv", "data/appointments.csv"):
                    print("Appointment booked successfully!")
                else:
                    print("Failed to book the appointment. Try again.")

            elif appointment_choice == "2":  # Cancel an appointment
                date = input("Enter appointment date (YYYY-MM-DD): ").strip()
                start_time = input("Enter appointment start time (HH:MM): ").strip()

                if user.manage_appointments("data/appointments.csv", "cancel", user.username, date, start_time):
                    print("Appointment cancelled successfully!")
                else:
                    print("Failed to cancel the appointment.")
            else:
                print("Invalid choice.")
        elif patient_choice == '5':
            confirm = input("Confirm delete account? (yes/no): ")
            if confirm.lower() == "yes":
                user.delete_from_csv()
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
        mood_entry.save_mood_entry()
        
        display_mood_history(user.username)
    else:
        print("Invalid mood selection.")

def display_mood_history(username):
    print("\nYour recent mood history:")
    history = MoodEntry.get_user_mood_history(username)
    if not history.empty:
        print(history[['timestamp', 'color_code', 'comments']].head())
