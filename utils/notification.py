import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv

def send_email_notification(recipient_email, subject, message):
    """
    Send an email notification to the recipient.
    """
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-email@gmail.com"
        sender_password = "your-email-password"  


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
