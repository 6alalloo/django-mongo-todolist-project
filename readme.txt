Ensure Python and MongoDB are installed on the PC.
ensure the environment variable "C:\Program Files\MongoDB\Server\8.0\bin" is set in the machine's environment variables
# Change the 8.0 to whatever version of MongoDB you have.


open the ToDoListProject folder.
Run "python -m venv TDLenv"
open the virtual environment with "TDLenv/Scripts/activate"
change directory with "cd todolist_project"
run "pip install -r requirements.txt" to get all the necessary dependancies
in a seperate terminal, enter the virtual environment, change to todolist_project, and run the command "mongod" to have the database running in the background.
create a superuser with "python manage.py createsuperuser"
after creating the superuser, log in to the admin page by running "python manage.py runserver" and then adding /admin to the end of the url.
"127.0.0.1:8000/admin"
login with the created superuser, and click on departments. create a department of your liking.
go back a page, and go to profiles, assign the department to the user, and make it a department manager for testing purposes.
Department managers can only be assigned through the admin dashboard, and departments can only be created through it too. This is to simulate a real business scenario.
After creating the profile, you can go back to the normal page "127.0.0.1:8000" and login with the new user. 
From there, you can use the website's full features.
