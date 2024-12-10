import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import configparser
import os


def load_email_config(config_file="email_config.ini"):
    """
    Load SMTP configuration from an INI file.
    """
   
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    
    config = configparser.ConfigParser()
    config.read(config_path)
    smtp_settings = config["SMTP"]
    return {
        "smtp_server": smtp_settings.get("smtp_server"),
        "smtp_port": smtp_settings.getint("smtp_port"),
        "smtp_ssl": smtp_settings.get("smtp_ssl"),
        "auth_username": smtp_settings.get("auth_username"),
        "auth_password": smtp_settings.get("auth_password"),
    }


def send_email_notification(recipient_email, subject, message, config_file="email_config.ini"):
    """
    Send an email notification to the recipient using configuration from an INI file.
    """
    try:
        # Load email configuration
        config = load_email_config(config_file)
        smtp_server = config["smtp_server"]
        smtp_port = config["smtp_port"]
        sender_email = config["auth_username"]
        sender_password = config["auth_password"]

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print(f"Notification sent to {recipient_email}.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")

def get_email_by_username(username, file_path="data/user_data.csv"):
    """
    Retrieve the email address for a given username from user_data.csv.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return row['email']
    except FileNotFoundError:
        print(f"Error: User data file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading user data: {e}")
    return None
