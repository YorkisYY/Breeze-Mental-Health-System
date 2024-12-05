import pandas as pd
from datetime import datetime


COMMENTS_FILE = "data/comments.csv"
APPOINTMENTS_FILE = "data/appointments.csv"


def comment(patient_username):
    available_appointments, option_map = get_available_appointments(patient_username)

    # If no available appointments, exit the function
    if available_appointments.empty:
        return

    try:
        # Prompt the user to select an appointment
        option = int(input("Select an appointment option to comment on (1, 2, ...): "))

        # Validate the user's selection
        if option not in option_map:
            print("Invalid option selected.")
            return

        # Retrieve the selected appointment details
        selected_appointment = available_appointments.iloc[option_map[option]]
        appointment_id = selected_appointment["id"]
        mhwp_username = selected_appointment["mhwp_username"]
        appointment_datetime = selected_appointment["datetime"].strftime("%Y-%m-%d %H:%M:%S")

        # Prompt the user for rating and comment
        rating = float(input("Enter your rating (0-5): "))
        comment_text = input("Enter your comment: ")

        # Add the comment to the comments file
        add_comment(patient_username, mhwp_username, rating, comment_text, appointment_id, appointment_datetime)
    except ValueError:
        
        # Handle invalid input
        print("Invalid input. Please select a valid option.")



            
            
def add_comment(patient_username, mhwp_username, rating, comment, appointment_id, appointment_datetime):
    """
    Add a patient's evaluation (rating and comment) of the MHWP to the comments file and link it to a specific appointment.
    """
    try:
        # Validate rating range
        if not (0 <= rating <= 5):
            print("Invalid rating. Please provide a rating between 0 and 5.")
            return

        # Prepare comment data
        comment_data = {
            "patient_username": patient_username,
            "mhwp_username": mhwp_username,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "appointment_id": appointment_id,
            "appointment_datetime": appointment_datetime,
        }

        # Read or create the comments file
        try:
            comments_df = pd.read_csv(COMMENTS_FILE)
            
            # Check if the appointment has already been commented on
            if not comments_df.empty and appointment_id in comments_df["appointment_id"].values:
                print("You have already commented on this appointment.")
                return

            # Append new data if the file is not empty
            comments_df = pd.concat([comments_df, pd.DataFrame([comment_data])], ignore_index=True)
        except FileNotFoundError:
            # Create a new file if it doesn't exist
            comments_df = pd.DataFrame([comment_data])

        # Save the comment
        comments_df.to_csv(COMMENTS_FILE, index=False)
        print("Comment added successfully!")

    except Exception as e:
        print(f"Error adding comment: {e}")


def get_available_appointments(patient_username):
   
    try:
        appointments = pd.read_csv(APPOINTMENTS_FILE)

        patient_appointments = appointments[appointments["patient_username"] == patient_username].copy()

        if patient_appointments.empty:
            print("No appointments found for this patient.")
            return pd.DataFrame(), {}

        now = datetime.now()
        patient_appointments["datetime"] = pd.to_datetime(
            patient_appointments["date"] + " " + patient_appointments["timeslot"].str.split("-").str[0]
        )
        available_appointments = patient_appointments[
            (patient_appointments["status"] == "confirmed") & (patient_appointments["datetime"] < now)
        ].reset_index(drop=True)

        if available_appointments.empty:
            print("No appointments available for commenting.")
            return pd.DataFrame(), {}

        print("\nAvailable appointments for commenting:")
        print("--------------------------------------------------------------")
        print("Option | Appointment ID | Date       | Time      | MHWP Username")
        print("--------------------------------------------------------------")
        option_map = {}
        for idx, (i, row) in enumerate(available_appointments.iterrows(), start=1):
            print(f"{idx:<6} | {row['id']:<14} | {row['date']} | {row['timeslot']} | {row['mhwp_username']}")
            option_map[idx] = i
        print("--------------------------------------------------------------")

        return available_appointments, option_map

    except Exception as e:
        print(f"Error loading appointments: {e}")
        return pd.DataFrame(), {}




def view_comments(mhwp_username):
    """
    View all comments for a specific MHWP.
    """
    try:
        # Load the comments file
        comments_df = pd.read_csv(COMMENTS_FILE)
        
        # Filter comments belonging to the MHWP
        mhwp_comments = comments_df[comments_df["mhwp_username"] == mhwp_username]

        if mhwp_comments.empty:
            print(f"No comments found for MHWP '{mhwp_username}'.")
            return
        else:
            print(f"\nComments for MHWP '{mhwp_username}':")
            print("------------------------------------------------------------------")
            print("Patient      | Rating | Comment                               | Timestamp")
            print("------------------------------------------------------------------")
            for _, row in mhwp_comments.iterrows():
                print(f"{row['patient_username']:<12} | {row['rating']:<6} | {row['comment']:<40} | {row['timestamp']}")
            print("------------------------------------------------------------------")

    except FileNotFoundError:
        print("No comments file found. Please initialize it first.")
    except Exception as e:
        print(f"Error viewing comments: {e}")
