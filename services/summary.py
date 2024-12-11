import pandas as pd
import os
from tabulate import tabulate
from datetime import datetime, timedelta
from config import ASSIGNMENTS_DATA_PATH, APPOINTMENTS_DATA_PATH, PATIENTS_DATA_PATH, MHWP_DATA_PATH



# Function to read CSV files and handle specific errors
def read_csv(file_path):
    """
    Reads a CSV file and handles specific errors related to file loading.

    Arguments:
    file_path (str): Path to the CSV file to be read.

    Returns:
    pandas.DataFrame: The data from the CSV file as a DataFrame if the file is read successfully.

    Raises:
    FileNotFoundError: If the file does not exist at the specified path.
    ValueError: If the file is empty or contains invalid data.
    """

    # Check if the file exists at the specified path
    if not os.path.exists(file_path):
        # Raise a FileNotFoundError if the file is not found
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    try:
        # Try to read the CSV file using pandas and return the DataFrame
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:  # If the file is completely empty
        # Raise a ValueError if the file is empty
        raise ValueError(f"Error: File '{file_path}' is empty.")
    except pd.errors.ParserError: # If the file format is invalid
        # Raise a ValueError if the file contains invalid data
        raise ValueError(f"Error: File '{file_path}' contains invalid data.")
    except Exception as e:
        # Catch any other unexpected errors and raise a ValueError with the error message
        raise ValueError(f"Error loading file '{file_path}': {e}")


# Function to load data from assignments
def load_assignments():
    try:
        # Attempt to read the assignments data from a CSV file
        return read_csv(ASSIGNMENTS_DATA_PATH)
    except Exception as e:
        # If an error occurs, print the error message and return an empty DataFrame
        print(e)
        return pd.DataFrame() # Return an empty DataFrame to ensure the safety of the next stages


# Function to load data from appointments
def load_appointments():
    try:
        # Attempt to read the appointments data from a CSV file
        return read_csv(APPOINTMENTS_DATA_PATH)
    except Exception as e:
        # If an error occurs, print the error message and return an empty DataFrame
        print(e)
        return pd.DataFrame() # Return an empty DataFrame to ensure the safety of the next stages

# Function to get the start and end dates of the current week
def thisWeek():
    # Get the current date
    today = datetime.today()
    # Calculate the start of the week (Monday)
    week_start = today - timedelta(days=today.weekday())
    # Calculate the end of the week (Sunday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


# Function to get bookings based on status and date range
def get_bookings(appointments, start_date, end_date, status):
    """
    Filters the appointments based on the given status and date range and returns the counts of each status.

    Arguments:
    appointments (pandas.DataFrame): DataFrame containing appointment data.
    start_date (datetime): The start date of the period to filter.
    end_date (datetime): The end date of the period to filter.
    status (str): The status to filter the appointments by ('all', 'confirmed', 'cancelled', 'pending', or 'Separate statistics').

    Returns:
    pandas.Series: A series with the count of appointments grouped by MHWP (Mental Health and Wellbeing Practitioner) and status.
    """

    # Convert the 'date' column to datetime format
    appointments["date"] = pd.to_datetime(appointments["date"], format="%Y/%m/%d")

    # If the status is 'all', filter all appointments within the date range
    if status == "all":
        # Filter appointments within the date range
        filtered_appointments = appointments[
            (appointments["date"] >= start_date) &
            (appointments["date"] <= end_date)
            ]
        # Count the occurrences of each status
        status_counts = filtered_appointments['status'].value_counts()

    # If the status is 'Separate statistics', group by MHWP and status, and count the number of appointments
    elif status == "Separate statistics":
        # Filter appointments within the date range
        filtered_appointments = appointments[
            (appointments["date"] >= start_date) &
            (appointments["date"] <= end_date)
            ]
        # Group appointments by 'mhwp_username' and 'status', count the occurrences, and reshape the result into a table
        status_counts = filtered_appointments.groupby(['mhwp_username', 'status']).size().unstack(fill_value=0)

    else:
        # For specific statuses (e.g., 'confirmed', 'cancelled', 'pending'), filter by both status and date range
        filtered_appointments = appointments[
            (appointments["status"] == status) &
            (appointments["date"] >= start_date) &
            (appointments["date"] <= end_date)
            ]
        # Count the number of appointments for each MHWP with the given status
        status_counts = filtered_appointments["mhwp_username"].value_counts()

    return status_counts


# Function to print the result of bookings in a formatted table
def print_result(result):
    """
    Prints the result (either a pandas Series or DataFrame) in a tabular format.

    Arguments:
    result (pandas.Series or pandas.DataFrame): The result to be printed.
    """

    # If the result is a Series, convert it to a DataFrame
    if isinstance(result, pd.Series):
        result_df = result.to_frame(name='count')
    else:
        result_df = result  # If it's already a DataFrame, use it as-is

    print()
    # Use the 'tabulate' module to print the DataFrame in a grid format
    print(tabulate(result_df, headers='keys', tablefmt='grid', showindex=True))


# Function to get a valid date input from the user
def get_valid_date_input(prompt):
    """
    Continuously prompts the user for a valid date in the format YYYY/MM/DD until a valid input is given.

    Arguments:
    prompt (str): The prompt message to show to the user.

    Returns:
    datetime: The valid date input by the user.
    """
    while True:
        # Get user input and remove extra spaces
        user_input = input(prompt).strip()
        try:
            # Try to convert the input string into a datetime object
            date = datetime.strptime(user_input, "%Y/%m/%d")
            return date  # Return the valid date
        except ValueError:
            # If the input is not in the correct format, display an error message
            print("Invalid date format. Please use YYYY/MM/DD format.")


def display_booking_summary():
    """
    Displays a summary of confirmed appointments for the current week,
    and allows the user to modify the time range and status of the summary.
    """

    try:
        # Load the appointments data from the file
        appointments = load_appointments()

        # Get the start and end date of the current week
        start_date, end_date = thisWeek()

        # Get the booking summary for confirmed appointments within the current week
        results = get_bookings(appointments, start_date, end_date, "confirmed")

        # Check if there are any results
        if results.empty:
            print("No summary data available.")
        else:
            print("Appointments confirmed for the current week")
            # Print the results in a tabular format
            print_result(results)

        # Start a loop to ask the user what they want to do next
        while True:
            print(f"\nWhat do you want to do next?")
            print("1. Modify the time range and status of the summary")
            print("2. Returning to main menu")

            # Get user's choice
            choice = input("Select an option (1-2): ").strip()

            if choice == "1":
                # If the user wants to modify the summary, prompt them to enter a new date range
                appointments = load_appointments()

                # Get the new start and end date from the user input
                start_date = get_valid_date_input("Enter start date (YYYY/MM/DD): ")
                end_date = get_valid_date_input("Enter end date (YYYY/MM/DD): ")
                start_date = datetime.strptime(start_date, "%Y/%m/%d")
                end_date = datetime.strptime(end_date, "%Y/%m/%d")

                # Check if the start date is later than the end date, if so, ask the user to try again
                if start_date > end_date:
                    print("Invalid date, please try again.")
                    continue

                # Get the status choice from the user
                status = input(
                    "Enter status (1-4), 1:cancelled, 2:confirmed, 3:pending, 4:all, 5:separate statistics): ")
                if status == "1":
                    results = get_bookings(appointments, start_date, end_date, "cancelled")
                elif status == "2":
                    results = get_bookings(appointments, start_date, end_date, "confirmed")
                elif status == "3":
                    results = get_bookings(appointments, start_date, end_date, "pending")
                elif status == "4":
                    results = get_bookings(appointments, start_date, end_date, "all")
                elif status == "5":
                    results = get_bookings(appointments, start_date, end_date, "Separate statistics")
                else:
                    print("Invalid choice, please try again.")

                # Print the updated results in a tabular format
                print_result(results)

            elif choice == "2":
                # If the user wants to return to the main menu, break out of the loop
                print("Returning to last menu.")
                break

            else:
                # If the user provides an invalid choice, prompt them to try again
                print("Invalid choice, please try again.")

    except Exception as e:
        # If there is an error while displaying the booking summary, print the error message
        print(f"Error displaying booking summary: {e}")


def display_summary():
    """
    Displays a menu to allow the user to choose what type of summary they want to see:
    - Booking summary
    - Information about MHWPs (Mental Health and Wellbeing Practitioners) and their patients
    """

    try:
        while True:
            # Display the main menu options
            print(f"\nWhat do you want to do?")
            print("1. See the summary of booking")
            print("2. Displays information about MHWPs and their patients")
            print("3. Returning to main menu")

            # Get user's choice from the menu
            type = input("Select an option (1-3): ").strip()

            if type == "1":
                # If the user selects '1', display the booking summary
                display_booking_summary()
            elif type == "2":
                # If the user selects '2', display MHWPs and their patients
                display_mhwp_summary()
                view_patients_for_mhwp()

            elif type == "3":
                # If the user selects '3', return to the main menu
                print("Returning to main menu.")
                break

            else:
                # If the user provides an invalid option, prompt them to try again
                print("Invalid choice, please try again.")

    except Exception as e:
        # If there is an error in displaying the summary, print the error message
        print(f"Error displaying summary: {e}")

def load_patients():
    """
    Loads the patient data from the CSV file.
    If an error occurs during loading, it prints the error and returns an empty DataFrame.
    """
    try:
        return read_csv(PATIENTS_DATA_PATH)  # Load patient data from the file
    except Exception as e:
        print(e)  # Print any error encountered during loading
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


def load_mhwp():
    """
    Loads the MHWP (Mental Health and Wellbeing Practitioner) data from the CSV file.
    If an error occurs during loading, it prints the error and returns an empty DataFrame.
    """
    try:
        return read_csv(MHWP_DATA_PATH)  # Load MHWP data from the file
    except Exception as e:
        print(e)  # Print any error encountered during loading
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


def get_patients_for_mhwp(mhwp_name):
    """
    Retrieves and displays the patients assigned to a specific MHWP based on their name.
    Displays the patients' information including username, symptoms, and registration date.
    """
    # Load patient and MHWP data
    patients = load_patients()
    mhwp = load_mhwp()

    # Find the MHWP information based on the provided name
    mhwp_info = mhwp[mhwp['username'] == mhwp_name]

    # If no information is found for the given MHWP name, print a message and exit
    if mhwp_info.empty:
        print(f"No information found for MHWP {mhwp_name}.")
        return

    # Extract the list of assigned patients for the MHWP
    assigned_patients = mhwp_info['assigned_patients'].values[0]
    assigned_patients_list = assigned_patients.split(',') if assigned_patients else []

    # If there are no assigned patients, notify the user
    if not assigned_patients_list:
        print(f"MHWP {mhwp_name} has no assigned patients.")
        return

    # Get the patients' information based on their usernames
    patients_assigned = patients[patients['username'].isin(assigned_patients_list)]

    # Reset index and drop the original index column
    patients_assigned = patients_assigned.reset_index(drop=True)

    # Display the information of the patients assigned to the MHWP
    print(f"Patients assigned to MHWP {mhwp_name}:")
    print(tabulate(patients_assigned[['username', 'symptoms', 'registration_date']], headers='keys', tablefmt='grid', showindex=False))


def calculate_mhwp_patient_counts():
    """
    Calculates and returns the number of patients assigned to each MHWP along with their specialization.
    Returns a DataFrame containing MHWP names, specializations, and patient counts.
    """
    # Load data
    mhwp = load_mhwp()
    patients = load_patients()
    assignments = load_assignments()

    # Initialize an empty list to store MHWP names and their assigned patient counts
    mhwp_patient_counts = []

    # Iterate through each MHWP in the dataset
    for _, mhwp_row in mhwp.iterrows():
        mhwp_name = mhwp_row['username']
        mhwp_major = mhwp_row['major']

        # Get the list of assigned patients for the current MHWP
        assigned_patients = mhwp_row['assigned_patients']
        if pd.isna(assigned_patients):
            patient_count = 0
        else:
            assigned_patients_list = assigned_patients.split(',')
            patient_count = len(assigned_patients_list)

        # Add the data to the list
        mhwp_patient_counts.append([mhwp_name, mhwp_major, patient_count])

    # Convert the list into a DataFrame
    mhwp_summary_df = pd.DataFrame(mhwp_patient_counts, columns=['MHWP Name', 'Specialization (Major)', 'Assigned Patient Count'])

    # Return the DataFrame containing the MHWP summary
    return mhwp_summary_df


def display_mhwp_summary():
    """
    Displays the summary of MHWPs including their specialization and the number of patients assigned.
    If no data is available, it notifies the user.
    """
    mhwp_summary_df = calculate_mhwp_patient_counts()

    # If the summary DataFrame is empty, notify the user
    if mhwp_summary_df.empty:
        print("No MHWP data available.")
        return

    # Print the MHWP summary in a tabular format
    print("\nMHWP Summary (including specialization and number of patients assigned):")
    print(tabulate(mhwp_summary_df, headers='keys', tablefmt='grid', showindex=False))


def view_patients_for_mhwp():
    """
    Allows the user to view patients assigned to a specific MHWP.
    The user can enter the MHWP name or enter '0' to exit.
    Validates the input to ensure the entered name exists and is correct.
    """
    while True:
        try:
            # Ask the user to input the name of the MHWP whose patients they want to view
            print("Please enter whose patient you would like to see.")
            mhwp_name = input("Please type the name of MHWP or enter '0' to exit: ")

            # If the user enters '0', exit the loop and return to the main menu
            if mhwp_name == "0":
                print("Exiting patient view.")
                break  # Exit the loop

            # Ensure the user input is not empty
            if not mhwp_name:
                print("Error: MHWP name cannot be empty. Please try again.")
                continue

            # Load the list of all valid MHWP names
            mhwp_data = load_mhwp()
            valid_mhwp_names = mhwp_data['username'].tolist()

            # Check if the entered MHWP name is valid
            if mhwp_name not in valid_mhwp_names:
                print(f"Error: '{mhwp_name}' is not a valid MHWP. Please enter a valid MHWP name.")
                continue

            # Retrieve and display the patients assigned to the entered MHWP
            get_patients_for_mhwp(mhwp_name)

        except ValueError as ve:
            # Catch any value errors and print the error message
            print(f"Error: {ve}")
        except Exception as e:
            # Catch any other unexpected errors and print the error message
            print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':  # This block of code will only be executed when the script is run directly, not when it's imported as a module.

    # 1. View the patients assigned to a specific MHWP (Mental Health Worker)
    view_patients_for_mhwp()

    # 2. Display the summary for the MHWP, including workload and patient statistics
    display_mhwp_summary()

    # 3. Show a summary of the appointments, which may include appointment counts, statuses, etc.
    display_booking_summary()

    # 4. Retrieve patients assigned to a specific MHWP ('hougege') and display their details
    get_patients_for_mhwp('hougege')

    # 5. Display the overall summary report, which might include general patient health statistics or MHWP activity
    display_summary()

    # 6. Load the appointments data and store it in the variable 'appointments'
    appointments = load_appointments()

