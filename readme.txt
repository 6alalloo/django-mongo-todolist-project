Ensure Python and MongoDB are installed on the PC.
ensure the environment variable "C:\Program Files\MongoDB\Server\8.0\bin" is set in the machine's environment variables
# Change the 8.0 to whatever version of MongoDB you have.
ensure the directory for the MongoDB database exists, if not, create it with (for example)"mkdir C:\data\db"




open the Main folder.
Run "python -m venv TDLenv"
open the virtual environment with "TDLenv/Scripts/activate"
run "pip install -r requirements.txt" to get all the necessary dependancies
# if pip is buggy, run "python -m pip install --force-reinstall pip"
in a seperate terminal, enter the virtual environment, change to todolist_project, and run the command "mongod" to have the database running in the background.
in a 3rd terminal, run the command "mongosh" to connect to the mongo shell and the database. 
after connecting to the mongo shell, run "use TDLdb"
create a superuser with "python manage.py createsuperuser"
after creating the superuser, log in to the admin page by running "python manage.py runserver" and then adding /admin to the end of the url.
"127.0.0.1:8000/admin"
login with the created superuser, and click on departments. create a department of your liking.
go back a page, and go to profiles, assign the department to the user, and make it a department manager for testing purposes.
Department managers can only be assigned through the admin dashboard, and departments can only be created through it too. This is to simulate a real business scenario.
After creating the profile, you can go back to the normal page "127.0.0.1:8000" and login with the new user. 
From there, you can use the website's full features.
