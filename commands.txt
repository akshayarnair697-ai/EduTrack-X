python -m venv EduEnv
EduEnv\Scripts\activate
pip install django
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 
