# Setup 

(assumes Windows Powershell, if you are using bash scripts or Linux replace `python` with `python3`

### if you do not have one, create a python venv outside your working directory:

`python -m venv venv`

### pull the latest version of the repository:

`git pull https://github.com/jayp090/OpenSky`

or, if you already have a previous version, cd into that directory and use `git pull`

activate your python venv with `python3 {VENV}/Scripts/activate`
(if you are using Powershell you may have to change execution policy with `set-executionpolicy unrestricted process`)

`cd` into ~/OpenSky/OpenSky

pip install all dependencies:

`pip install -r requirements.txt`

### Run setup commands for the server:

`python manage.py migrate`, then

`python manage.py seed_data`, then

`python manage.py createsuperuser`

### Recommended admin user setup:

username: `admin`

email: `Admin@sky.uk`

password: `Admin@1234`

then, run the server:

`python manage.py runserver`

### Default user details for testing:

email: `user@sky.uk`

password: `User@1234`
