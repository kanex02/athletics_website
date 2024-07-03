cd /D "%~dp0"
git config --global user.name "Kane Xie"
git config --global user.email "16365@burnside.school.nz"
git pull
python -m venv env
call venv\scripts\activate
set FLASK_APP=signup.py
cmd /k
