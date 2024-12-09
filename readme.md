WHAT ARE WE WORKING ON !!!!-----------------------------------------------------
## 13-th Commit: schedule management and auto update
----------
**Arthur: 2024_12_09 07:39**
1. add schedule template management for mhwp. Now the mhwp have more freedom in create, update, delete schedule template. 
2. add auto update for mhwp schedule based on the schedule template. up to 4 weeks ahead.
3. change multiple schedule table display for better formatting.
4. modularize the mhwp code for better readability.

## 12-th Commit: disable/enable user account
----------
**Arthur: 2024_12_03 11:19**
1. add confirmation for the admin before cleaning up the mhwp schedule data.(need further cleaning by Desheng)
2. add user account status management for admin. changed files: 
model/admin.py, model/user_account_management/user_data_manage.py, services/login.py
3. add list_all_users() in utils to list all users from mhwp and patients to select one.

## Eleventh Commit
----------
**Chao-Wei: 2024_11_29 2:42**
1. Add up the mhwp.csv for the future upcoming feature.
2. the mhwp.csv would be simlutaneously updated with the user_data.csv.
3. Add up the symptoms attribution for patients and major for the mhwp.
4. new user registration would be required to choose their sypmtoms or major for the allocation of MHWP.
5. debugs 

## Tenth Commit
----------
**Chao-Wei: 2024_11_27 21:19**
1. Add up patient.csv for the future upcoming feature.
2. the patient.csv would be simlutaneously updated with the user_data.csv.
3. Add up the admin allocation function for patients.

## ninth Commit 
---------- 
**Shaoxiong Bai: 2024_11_26 21:19** 
### add up a series of new features
1. Add up a new patient comment and MHWP reading feature. Particularly, add new comment.py and commnents.csv
2. Add up a new patient journaling and MHWP reading feature. Particularly, add new journaling.py and patient_journaling.csv
3. Add up a new automatic questionnaire for patient mental health status and MHWP reading feature. Particularly, add new questionnaire.py and mental_assessments.csv  
4. Add up a new patient note for the MHWP feature. Particularly, add new patient_notes.csv
5. Add up a new meditation resource viewing feature. Particularly, add new meditation.py and meditation_resources.csv
6. Integrate the MHWP view patient records feature, including (1)view mood tracker, (2)view patient journaling, (3)view mental health assessments, and (4)add patient record. Particularly, add a brand new patient_records.py file
7. Add up a series of buttons in mhwp.py and patient.py files.

## Eigth Commit
----------
**CHAO-WEI : 2024_11_25 18:05**
### add up initial functions for mhwp calender and mhwp and debugs
1. add the function for mhwp calender


## Seventh Commit
----------
**CHAO-WEI : 2024_11_25 11:58**
### Fix up the bug of the previous commit related to logout within admin and mhwp, and modify the code of mhwp.py
1. remove the doctor.py, as the role is not needed 
2. remove the code related to doctor which would create bugs.
3. append the function that patients can change their username, email,emergency_email now
4. append the function that admin can change others' email, emergency_email.

## Sixth Commit
----------
**Arthur Hou: 2024_11_25 02:48**
### merge qxj's commit on mhwp's functions
1. change all instance of mhw to mhwp for naming consistency.
2. modify slight to mhwp.py for robustness.

## Fifth Commit
----------
**Arthur Hou: 2024_11_24 20:09**

### major change to the code structure, suggest doing subsequent development based on this commit.
1. Modularize the whole frame
    1. removed __init__.py from services. since the dependencies are now defined in each module themselves.
    2. Modularize user registration function register_user() to \\services\\registration.py
    3. Modularize login handling function handle_login() to \\services\\login.py; In handle_login() break each model's page into different function.
        * modularize admin's login page to handle_admin_menu() to \\model\\admin.py
        * modularize doctor's login page to handle_doctor_menu() to \\model\\doctor.py
        * modularize mhw's login page to handle_mhw_menu() to \\model\\mhwp.py
        * modularize patient's login page to handle_patient_menu() to \\model\\patient.py
2. Add patient mood tracking page.
2. Add patient mood tracking page.
    1. see \\services\\mood_tracking.py; the function is called when choose the corresponding selection in handle_patient_menu().
3. fix the bug that cause the program to exit after registration.
4. remove \\data\\patient_data.csv since it is redundant. All user info stored in \\data\\user_data.csv
5. place all the csv file path in config.py. The csv file path for classes and functions are easily controlled in this way. State 'from config import XXX_DATA_PATH' at the top of your code.
3. fix the bug that cause the program to exit after registration.
4. remove \\data\\patient_data.csv since it is redundant. All user info stored in \\data\\user_data.csv
5. place all the csv file path in config.py. The csv file path for classes and functions are easily controlled in this way. State 'from config import XXX_DATA_PATH' at the top of your code.

## Fourth Commit
----------
**CHAO-WEI:**

- 1. Added roles of MHWP, Doctor into menu
- 2. Change the entire frame

## Third Commit
----------
**CHAO-WEI:**

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
**CHAO-WEI:**

- 1. Removed the GUI file as we don't want to use it.
- 2. Created the basic functionality of the program in `user` and implemented the entry logic in the main functionality.
- 3. After testing, the table can be created and data can be inserted into the table.
- 4. The program can run, allowing the username and password to be compared with data in the CSV file.

**Date:** 2024.11.14.1:04
## First commit
----------
**CHAO-WEI:**

- 1. Create the project on GitHub. Commit the starter code from moodle.

**Date:**2024.11.11 1:06