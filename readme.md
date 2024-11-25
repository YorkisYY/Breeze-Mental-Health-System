## Fifth Commit
----------
**Arthur Hou: 2024_11_24 20:09**

# major change to the code structure, suggest doing subsequent development based on this commit.
- 1. Modularize the whole frame
    1. removed __init__.py from services. since the dependencies are now defined in each module themselves.
    2. Modularize user registration function register_user() to \\services\\registration.py
    3. Modularize login handling function handle_login() to \\services\\login.py; In handle_login() break each model's page into different function.
        * modularize admin's login page to handle_admin_menu() to \\model\\admin.py
        * modularize doctor's login page to handle_doctor_menu() to \\model\\doctor.py
        * modularize mhw's login page to handle_mhw_menu() to \\model\\mhwp.py
        * modularize patient's login page to handle_patient_menu() to \\model\\patient.py
- 2. Add patient mood tracking page.
    1. see \\services\\mood_tracking.py; the function is called when choose the corresponding selection in handle_patient_menu().
- 3. fix the bug that cause the program to exit after registration.
- 4. remove \\data\\patient_data.csv since it is redundant. All user info stored in \\data\\user_data.csv
- 5. place all the csv file path in config.py. The csv file path for classes and functions are easily controlled in this way. State 'from config import XXX_DATA_PATH' at the top of your code.

## Fourth Commit
----------
**York Tseng:**

- 1. Added roles of MHWP, Doctor into menu
- 2. Change the entire frame

## Third Commit
----------
**York Tseng:**

- 1. Added the admin function which can allow admin to manage other users's data such as delete, update.
- 2. user now can cancel their own account, and the admin can delete the user's data.
- 3. admin should insert the code to login which is 0000
- 4. The program can run, allowing the username and password to be compared with data in the CSV file
- 5. user can change their own username and password 
- 6. registation would compare the username with the data in the CSV file, avoiding the same username.
- 7. create the __intit__ file to form the package file 
- 8. !need update for MHWP function!

## Second Commit
----------
**York Tseng:**

- 1. Removed the GUI file as we don't want to use it.
- 2. Created the basic functionality of the program in `user` and implemented the entry logic in the main functionality.
- 3. After testing, the table can be created and data can be inserted into the table.
- 4. The program can run, allowing the username and password to be compared with data in the CSV file.

**Date:** 2024.11.14.1:04
## First commit
----------
**York Tseng:**

- 1. Create the project on GitHub. Commit the starter code from moodle.

**Date:**2024.11.11 1:06