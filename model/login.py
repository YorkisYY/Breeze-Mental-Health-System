import pandas as pd
from model.user import User  

def login_user(file_path):
   """Authenticate and login user.
   Args:
       file_path: Path to user data CSV file
   Returns:
       User object if login successful, None otherwise
   """
   username = input("Enter username: ").strip()
   password = input("Enter password: ").strip()
   
   # Create user object with temporary role
   user = User(username, password, "temp")
   
   # Verify credentials
   if user.load_from_csv(file_path):
       hashed_password = user.hash_password(password) 
       if user.password == hashed_password:
           print(f"Login successful! Welcome, {user.username}!")
           return user
       else:
           print("Incorrect password.")
   else:
       print("User does not exist.")
   return None