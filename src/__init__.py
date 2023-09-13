from decouple import config
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import pickle

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))



short_model_path = "models/logistic_regression_model.pkl"
short_vectorizer_path = "models/vectorizer.pkl"

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), short_model_path)
vectorizer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), short_vectorizer_path)

dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tweets_dataset.csv')


def load_model_and_vectorizer(model_path, vectorizer_path):
    ''' 
    Parameters: model_path and vectorizer_path
    Logic: It loads and returns the model and vectorizer using the specified path
    '''

    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    with open(vectorizer_path, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    return model, vectorizer

# Load our sentiment analysis model and vectorizer for later use
model, vectorizer = load_model_and_vectorizer(model_path, vectorizer_path)

def predict_text_sentiment(text = ''):
    '''
    Parameters: the text to be analyzed
    Logic: it loads the model and vectorizer and performs text sentiment analysis
    '''
    text_vec = vectorizer.transform([text])
    # Make predictions using the loaded model
    prediction = model.predict(text_vec)[0] 
    return {'sentiment': prediction}

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Registering blueprints
from src.accounts.views import accounts_bp
from src.core.views import core_bp
from src.dashboard.views import dashboards_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)
app.register_blueprint(dashboards_bp)

from src.accounts.models import User
from src.dashboard.models import Tweet
from src.dashboard.models import Feedback

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


########################
#### error handlers ####
########################


@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500




