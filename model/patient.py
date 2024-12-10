import os
from services.mood_tracking import MoodEntry
from services.meditation import handle_search_meditation
from services.comment import comment
from services.questionnaire import submit_questionnaire,remind_to_complete_questionnaire
from services.journaling import enter_journaling
from services.patient_records import view_my_records
from utils.notification import send_email_notification, get_email_by_username
import pandas as pd
from tabulate import tabulate  
from os.path import exists
import csv
from config import *
from .patient_management.patient_account import handle_account_management
from .patient_management.health_wellbeing import handle_health_wellbeing
from .patient_management.appointment import *
def handle_patient_menu(user):
    remind_to_complete_questionnaire(user.username)

    while True:
        print("\nPatient Options:")
        print("1. Account Management")
        print("2. Health & Wellbeing")
        print("3. Appointments & Comments")
        print("4. Logout")

        main_choice = input("Select an option (1-4): ").strip()

        if main_choice == '1':  # Account Management
            handle_account_management(user)
                                                
        elif main_choice == '2':  
            handle_health_wellbeing(user)

        elif main_choice == '3':  # Appointments & Records
            while True:
                print("\nAppointments & Comments:")
                print("1. Book/Cancel Appointment")
                print("2. Check Appointments")
                print("3. Leave a Comment for Your MHWP")
                print("4. Back to Main Menu")

                records_choice = input("Select an option (1-4): ").strip()

                if records_choice == '1':
                    import pandas as pd
            
                    while True:
                        print("\nBook/Cancel Appointment:")
                        print("1. Book an appointment")
                        print("2. Cancel an appointment")
                        print("3. Return to main menu")

                        appointment_choice = input("Select an option (1/2/3): ").strip()

                        if appointment_choice == "1":  # Book an appointment
                            book_appointment_with_schedule(user, "data/mhwp_schedule.csv", "data/assignments.csv", "data/appointments.csv")

                        elif appointment_choice == "2":  # Cancel an appointment
                            cancel_appointment_with_display(user, "data/mhwp_schedule.csv", "data/appointments.csv")
                
                        elif appointment_choice == "3":  # Return to main menu
                            print("Returning to main menu...")
                            break
                        
                elif records_choice == '2':
                    while True:
                        display_upcoming_appointments_with_mhwp(
                            user.username, 
                            "data/appointments.csv", 
                            "data/assignments.csv"
                        )
                
                        print("\nPress '1' to return to the main menu.")
                        return_choice = input("Enter your choice: ").strip()
                
                        if return_choice == '1':
                            break  # Return to main menu
                        else:
                            print("Invalid choice. Please press '1' to return to the main menu.")

                elif records_choice == '3':
                    comment(user.username)

                elif records_choice == '4':
                    break  # Return to main menu
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == '4':  # Logout
            print("Logging out.")
            break

        else:
            print("Invalid choice, please try again.")