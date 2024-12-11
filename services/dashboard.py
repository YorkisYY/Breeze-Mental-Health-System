import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from services.trainModal import compute_tfidf
from config import MOOD_DATA_PATH, PATIENTS_DATA_PATH
from services.patient_records import patient_record_menu
from tabulate import tabulate

# read csv files
def read_csv(file_path):
    """
    Reads a CSV file and handles specific errors such as file not found, empty data, and invalid data format.
    """
    if not os.path.exists(file_path):  # Check if the file exists
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")  # Raise an error if the file does not exist
    try:
        return pd.read_csv(file_path)  # Attempt to read the CSV file
    except pd.errors.EmptyDataError:  # If the file is empty, raise an error
        raise ValueError(f"Error: File '{file_path}' is empty.")
    except pd.errors.ParserError:  # If the file has invalid data format, raise an error
        raise ValueError(f"Error: File '{file_path}' contains invalid data.")


# load data from patients
def load_patient_data():
    """
    Loads the patient data from the CSV file using the read_csv function.
    If an error occurs, prints the error and returns an empty DataFrame.
    """
    try:
        return read_csv(PATIENTS_DATA_PATH)  # Load patient data from the CSV file
    except Exception as e:
        print(e)  # Print any error encountered during loading
        return pd.DataFrame()  # Return an empty DataFrame in case of an error (to ensure the program continues safely)


# load data from mood
def load_mood_data():
    """
    Loads mood data from the CSV file using the read_csv function.
    If an error occurs, prints the error and returns an empty DataFrame.
    """
    try:
        return read_csv(MOOD_DATA_PATH)  # Load mood data from the CSV file
    except Exception as e:
        print(e)  # Print any error encountered during loading
        return pd.DataFrame()  # Return an empty DataFrame in case of an error (to ensure the program continues safely)


def get_patients_by_mhwp(mhwp_username):
    """
    Retrieves patients that are assigned to a specific MHWP based on the provided username.
    Returns a DataFrame of patients assigned to the given MHWP.
    """
    patients = load_patient_data()  # Load the patient data
    if patients.empty:  # Check if the patient data is empty (i.e., there are no patient records)
        print("No patient data available.")  # If no data is available, notify the user
        return pd.DataFrame()  # Return an empty DataFrame to avoid errors
    return patients[patients["assigned_mhwp"] == mhwp_username]  # Filter and return patients assigned to the specified MHWP


# more information about patients
def get_patient_mood_data(username):
    """
    Retrieves the mood data of a specific patient based on their username.
    Returns a DataFrame containing the patient's mood records.
    """
    moods = load_mood_data()  # Load the mood data
    if moods.empty:  # Check if the mood data is empty
        print("No mood data available.")  # If no data is available, notify the user
        return pd.DataFrame()  # Return an empty DataFrame to avoid errors
    return moods[moods["username"] == username]  # Filter and return the mood data for the specified patient

# Mapping of color codes to mood scores
color_code_to_score = {
    "Green": 1,    # Green corresponds to a score of 1
    "Blue": 2,     # Blue corresponds to a score of 2
    "Yellow": 3,   # Yellow corresponds to a score of 3
    "Orange": 4,   # Orange corresponds to a score of 4
    "Red": 5,      # Red corresponds to a score of 5
}

# Mapping of color codes to their respective colors for the pie chart
color_mapping = {
    "Green": "green",    # Green maps to the color green
    "Blue": "blue",      # Blue maps to the color blue
    "Yellow": "yellow",  # Yellow maps to the color yellow
    "Orange": "orange",  # Orange maps to the color orange
    "Red": "red"         # Red maps to the color red
}


def generate_summary(mhwp_username):
    """
    Generates a summary of the mood data for all patients assigned to the given MHWP username.
    The summary includes the total number of mood entries, last recorded mood, and average mood score for each patient.
    """
    try:
        patients = get_patients_by_mhwp(mhwp_username)  # Get the list of patients assigned to the given MHWP
        moods = load_mood_data()  # Load the mood data for all patients

        if patients.empty:  # If there is no patient data available
            print("No patient data available for summary.")
            return pd.DataFrame()  # Return an empty DataFrame if no patients are found

        summary = []  # Initialize a list to store the summary data for each patient

        # Iterate over each patient and generate the summary data
        for _, patient in patients.iterrows():
            username = patient["username"]  # Get the username of the patient
            mood_data = moods[moods["username"] == username]  # Filter mood data for this patient

            total_moods = len(mood_data)  # Count the total number of mood entries for the patient

            # If the patient has no mood entries, set "N/A" for the last mood and average mood
            if total_moods == 0:
                last_mood = "N/A"
                average_mood = "N/A"
            else:
                mood_data = mood_data.sort_values(by="timestamp", ascending=False)  # Sort mood entries by timestamp (latest first)

                last_mood = mood_data.iloc[0]["color_code"]  # Get the color code of the last recorded mood
                mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)  # Map color code to corresponding score
                average_mood = mood_data["mood_score"].mean()  # Calculate the average mood score for this patient

            # Append the summary data for the current patient to the list
            summary.append({
                "username": username,
                "Mood Entries": total_moods,
                "Last Mood": last_mood,
                "Average Mood Score": average_mood
            })

        return pd.DataFrame(summary)  # Return the summary as a DataFrame

    except KeyError as e:  # Handle missing columns in the data (e.g., incorrect column names)
        print(f"Data error: Missing column {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error
    except Exception as e:  # Handle any other unexpected errors
        print(f"Unexpected error during summary generation: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


def display_patient_summary_tabulate(summary_data):
    """
    Display patient summary using tabulate for better formatting.
    :param summary_data: List of dictionaries containing patient summary.
    """
    if summary_data.empty:  # Check if there is no data available
        print("No patient data available.")
        return

    print("Patient Summary:")
    print(tabulate(summary_data, headers="keys", tablefmt="grid"))  # Display the patient summary in a grid format using tabulate


def display_patient_summary(summary_data):
    """
    Display patient summary as a text table.
    :param summary_data: pandas.DataFrame containing patient summary information.
    """
    if summary_data.empty:  # Check if there is no data available
        print("No patient data available.")
        return

    print("Patient Summary:")
    print("-" * 60)  # Print a separator line
    print(summary_data.to_string(index=False))  # Print the DataFrame as a text table without the index
    print("-" * 60)  # Print another separator line


def plot_mood(patient_username):
    """
    Plot the mood trend and mood status distribution for a specific patient based on their mood data.
    :param patient_username: The username of the patient whose mood data is to be plotted.
    """
    try:
        moods = load_mood_data()  # Load mood data for all patients

        if moods.empty:  # If mood data is empty
            print("No mood data found.")
            return

        mood_data = moods[moods["username"] == patient_username]  # Filter mood data for the specific patient

        # If no mood data exists for the patient, print a message and exit
        if mood_data.empty:
            print(f"No mood data available for patient {patient_username}.")
            return

        # Sort the mood data by timestamp to ensure the mood entries are in chronological order
        mood_data = mood_data.sort_values(by="timestamp", ascending=True)

        # Map the color codes to corresponding mood scores
        mood_data["mood_score"] = mood_data["color_code"].map(color_code_to_score)

        try:
            # Plot the mood trend over time as a line chart
            plt.figure(figsize=(10, 5))  # Set the figure size
            plt.plot(mood_data["timestamp"], mood_data["mood_score"], label=f"{patient_username}'s Mood Trend",
                     marker='o')  # Plot mood scores with timestamps
            plt.xlabel("Time")
            plt.ylabel("Mood Score (1 = Green, 5 = Red)")  # Label the axes
            plt.title(f"Mood Trend for {patient_username}")  # Set the chart title

            # Format the timestamps to display as date and time (only the date part)
            formatted_dates = pd.to_datetime(mood_data["timestamp"])
            formatted_dates = formatted_dates.dt.strftime('%Y-%m-%d: %H:%M')  # Format the dates

            # Set the x-axis ticks as the formatted dates and rotate them for better readability
            plt.xticks(mood_data["timestamp"], formatted_dates, rotation=45)

            plt.yticks([1, 2, 3, 4, 5])  # Display integer labels for mood scores

            plt.legend()  # Show the legend
            plt.tight_layout()  # Ensure the layout is not overlapping
            plt.show()  # Display the plot
        except Exception as e:
            print(f"Error while plotting mood trend: {e}")  # Handle any errors that occur while plotting the mood trend

        try:
            # Generate a pie chart showing the distribution of mood states (color codes)
            mood_counts = mood_data["color_code"].value_counts()  # Count the occurrences of each color code
            # Map each mood state to a corresponding color for the pie chart
            colors = [color_mapping.get(x) for x in mood_counts.index]
            plt.figure(figsize=(7, 7))  # Set the figure size for the pie chart
            mood_counts.plot(kind='pie', autopct='%1.1f%%',
                             colors=colors,  # Use the color mapping for mood states
                             startangle=90, counterclock=False)  # Set the starting angle and counter-clockwise direction
            plt.title("Mood Status Distribution")  # Set the title of the pie chart
            plt.ylabel("")  # Remove the y-axis label for cleaner display
            plt.show()  # Display the pie chart
        except Exception as e:
            print(f"Error while generating mood pie chart: {e}")  # Handle any errors while generating the pie chart

    except Exception as e:
        print(f"Error while generating mood trend plots: {e}")  # Handle any errors during the process


# Load the emotion model
with open('emotion_model.pkl', 'rb') as f:
    model = pickle.load(f)  # Load the pre-trained model

word_index = model['word_index']  # Extract word index from the model
idf = model['idf']  # Extract the IDF (Inverse Document Frequency) from the model
centers = model['centers']  # Extract cluster centers from the model

# Predict emotion for new data
def predict_emotion(new_document, word_index, idf, centers):
    """
    Predict the emotional cluster for a new document based on its TF-IDF features.
    :param new_document: The new text document (e.g., patient comment).
    :param word_index: Word index used for TF-IDF computation.
    :param idf: IDF values used for TF-IDF computation.
    :param centers: Cluster centers (centroids of the KMeans clusters).
    :return: Predicted cluster ID.
    """
    # Compute the TF-IDF features for the new document
    new_tfidf = compute_tfidf([new_document], word_index, idf)[0]  # Compute the TF-IDF vector for the new document

    # Compute the distance of the new document from each cluster center
    distances = np.linalg.norm(centers - new_tfidf, axis=1)  # Calculate Euclidean distance to each cluster center

    # Find the cluster with the minimum distance (most similar cluster)
    cluster_id = np.argmin(distances)
    return cluster_id


def display_dashboard(mhwp_username):
    """
    Display the patient dashboard, including summary data, and allow the user to interact with patient details.
    :param mhwp_username: The username of the mental health professional.
    """
    try:
        summary = generate_summary(mhwp_username)  # Generate patient summary
        if summary.empty:  # If there is no patient data, return
            print("No summary data available.")
            return

        display_patient_summary_tabulate(summary)  # Display the summary in tabular format

        while True:
            print(f"\nDo you want to see specific patient details or exit the dashboard?")
            print("1. See specific patient details")
            print("2. Returning to main menu")

            choice = input("Select an option (1-2): ").strip()  # User choice input
            if choice == "1":
                patient_name = input("Please type in the username of the patient:").strip()  # Get patient username
                plot_mood(patient_name)  # Plot the mood for the specific patient

                # Option to predict the patient's mood
                print("Would you like to predict the patient's mood? (Y/N)")
                predict_choice = input().strip()
                if predict_choice.lower() == "y":
                    try:
                        # Extract the most recent comment to predict the mood
                        last_mood_comment = get_patient_mood_data(patient_name)
                        last_mood_comment = last_mood_comment.iloc[-1]["comments"]  # Get the last mood comment
                        predicted_cluster = predict_emotion(last_mood_comment, word_index, idf, centers)  # Predict the cluster
                        mood_labels = ["Green", "Blue", "Yellow", "Orange", "Red"]  # Mood color labels
                        print(f"Predicted mood for {patient_name}: {mood_labels[predicted_cluster]}")
                    except Exception as e:
                        print(f"Error during prediction: {e}")  # Error handling during prediction

                print("Do you want to see more information about the patient?(Y/N)")

                while True:
                    isSee = input()
                    if isSee == "Y":
                        patient_record_menu(patient_name, mhwp_username)  # Show detailed patient records
                        break
                    elif isSee == "N":
                        break
                    else:
                        print("Invalid choice, please try again.")  # Handle invalid input

            elif choice == "2":
                print("Returning to main menu.")  # Return to the main menu
                break

            else:
                print("Invalid choice, please try again.")  # Handle invalid input

    except Exception as e:
        print(f"Error displaying dashboard: {e}")  # Handle any errors during dashboard display


if __name__ == '__main__':  # This block of code will only be executed when the script is run directly, not when it's imported as a module.

    # 1. Display the dashboard for a specific MHWP ('hougege'), which includes patient and appointment details
    display_dashboard('hougege')

    # 2. Plot the mood trend for a specific patient ('houdidi3')
    plot_mood("houdidi3")

    # 3. Show the detailed patient record for 'houdidi3' managed by the MHWP ('hougege')
    patient_record_menu('houdidi3', 'hougege')
