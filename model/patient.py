import os
from services.mood_tracking import MoodEntry
from services.meditation import handle_search_meditation
from services.comment import add_comment
from services.questionnaire import submit_questionnaire

from utils.notification import send_email_notification, get_email_by_username

def handle_patient_menu(user):
    while True:
        print("\nPatient Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. Change email")
        print("4. Change emergency email")
        print("5. View Medical Records")
        print("6. Book/Cancel Appointment")
        print("7. Submit a Mood Questionnaire")
        print("8. Leave a comment for your MHWP")
        print("9. Explore Meditation Resources")
        print("10. Delete Account")
        print("11. Track Mood")
        print("12. Logout")
        
        patient_choice = input("Select an option (1-9): ")
        if patient_choice == '1':
            new_username = input("Enter new username: ").strip()
            user.update_info(new_username=new_username)
        elif patient_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)
        elif patient_choice == '3':  # new funcs to change email
            new_email = input("Enter new email: ").strip()
            if user.update_info(new_email=new_email):  
                print("Email updated successfully!")
            else:
                print("Failed to update email. Try again.")
        elif patient_choice == '4':  # new option for emergency email
            new_emergency_email = input("Enter new emergency email: ").strip()
            if user.update_info(new_emergency_email=new_emergency_email):
                print("Emergency email updated successfully!")
            else:
                print("Failed to update emergency email. Try again.")
        elif patient_choice == '5':
            print("Medical records feature coming soon...")

        elif patient_choice == '6':  # Book/Cancel appointment
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
                    # Notify MHW about the booking
                    mhwp_email = get_email_by_username(mhwp_username)
                    if mhwp_email:
                        subject = "New Appointment Booked"
                        message = (
                            f"Dear {mhwp_username},\n\n"
                            f"A new appointment has been booked by {user.username} on {date} at {start_time} - {end_time}.\n\n"
                            "Regards,\nMental Health Support System"
                        )
                        send_email_notification(mhwp_email, subject, message)
                        print("Notification email sent to the MHW.")
                    else:
                        print("Error: Could not retrieve MHW's email address.")
                else:
                    print("Failed to book the appointment. Try again.")

            elif appointment_choice == "2":  # Cancel an appointment
                date = input("Enter appointment date (YYYY-MM-DD): ").strip()
                start_time = input("Enter appointment start time (HH:MM): ").strip()

                if user.manage_appointments("data/appointments.csv", "cancel", user.username, date, start_time):
                    print("Appointment cancelled successfully!")
                    # Notify MHW about the cancellation
                    mhwp_email = get_email_by_username(mhwp_username)
                    if mhwp_email:
                        subject = "Appointment Cancelled"
                        message = (
                            f"Dear {mhwp_username},\n\n"
                            f"The appointment with {user.username} on {date} at {start_time} has been cancelled by the patient.\n\n"
                            "Regards,\nMental Health Support System"
                        )
                        send_email_notification(mhwp_email, subject, message)
                        print("Notification email sent to the MHW.")
                    else:
                        print("Error: Could not retrieve MHW's email address.")
                else:
                    print("Failed to cancel the appointment.")
            else:
                print("Invalid choice.")
                
        elif patient_choice == '7':  # 心理问卷
            submit_questionnaire(user.username)

        elif patient_choice == '8':  # 添加评论
            # 获取患者和 MHWP 的用户名（假设可以从 user 和 appointment 关联）
            mhwp_username = "dr_green"  # 从预约文件中获取
            comment = input("Enter your comment for your MHW: ").strip()
            add_comment(user.username, mhwp_username, comment) 
                   
        elif patient_choice == '9':  # 新增处理逻辑
            handle_search_meditation()  # 调用冥想资源功能
            
        elif patient_choice == '10':
            confirm = input("Confirm delete account? (yes/no): ")
            if confirm.lower() == "yes":
                user.delete_from_csv()
                print("Account deleted successfully.")
                break
            
        elif patient_choice == '11':
            handle_mood_tracking(user)
            
        elif patient_choice == '12':
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
