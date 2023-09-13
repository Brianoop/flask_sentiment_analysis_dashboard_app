# Flask Ukraine Russia War Sentiment Analysis
Blog Tutorial: https://ashutoshkrris.hashnode.dev/how-to-set-up-basic-user-authentication-in-a-flask-app

Project Demo: https://youtu.be/XxSESg89xEI


# HOW TO RUN PROJECT

To set environment variables, run:

On linux: source .env
On windows: call .env.bat



flask db init

flask db migrate

flask db upgrade

python manage.py run


To solve erros cause due to deleting existing migrations folder

python app.py db revision --rev-id e39d16e62810  

python app.py db migrate  

python app.py db upgrade