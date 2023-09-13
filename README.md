# Flask Ukraine Russia War Sentiment Analysis
This flask application displays concepts such as user authentication, responsive design, database connectivity using sqlite, environmmen configuration, sentiment analysis model integration and file IO.
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