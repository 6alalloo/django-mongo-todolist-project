Ensure Python, MongoDB and mongorestore are installed on the PC.
ensure the environment variable "C:\Program Files\MongoDB\Server\8.0\bin" is set in the machine's environment variables
# Change the 8.0 to whatever version of MongoDB you have.
ensure the environment variable "C:\Program Files\MongoDB\Tools\100\bin" is set.
ensure the directory for the MongoDB database exists, if not, create it with (for example)"mkdir C:\data\db"
Ensure the interpreter is the Virtual Environment's interpreter.




open the Main folder.
Run "python -m venv TDLenv"
open the virtual environment with "TDLenv/Scripts/activate"
run "pip install -r requirements.txt" to get all the necessary dependancies
# if pip is buggy, run "python -m pip install --force-reinstall pip"
restore the DB by running "mongorestore --db TDLdb <full\path\to\db\TDLdb>"
run "python manage.py makemigrations"
then run "python manage.py migrate"
create a superuser with "python manage.py createsuperuser"
after creating the superuser, log in to the admin page by running "python manage.py runserver" and then adding /admin to the end of the url.
"127.0.0.1:8000/admin"
login with the created superuser, and click on departments. create a department of your liking.
go back a page, and go to profiles, assign the department to the user, and make it a department manager for testing purposes.
#Optionally, when choosing the profile, make the user a part of the HR department and a manager of it, there is some ready-made test data there.
Department managers can only be assigned through the admin dashboard, and departments can only be created through it too. This is to simulate a real business scenario.
After creating the profile, you can go back to the normal page "127.0.0.1:8000" and login with the new user. 
From there, you can use the website's full features.
