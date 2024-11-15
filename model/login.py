import pandas as pd
from model.user import User  

def login_user(file_path):
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    user = User(username, password)
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
