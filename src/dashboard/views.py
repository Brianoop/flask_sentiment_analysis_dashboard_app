from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user

from src import bcrypt, db
from src.dashboard.models import Tweet, Feedback
from src import predict_text_sentiment
from src import dataset_path
import pandas as pd
import re

from datetime import datetime
import pytz

from flask_sqlalchemy import Pagination
from flask_wtf import FlaskForm
from wtforms import IntegerField

url = dataset_path

dashboards_bp = Blueprint("dashboards", __name__)

@dashboards_bp.route('/predict', methods=['GET'])
def predict_sentiment():
    try:
        text = request.args.get('text', 1, type=str)
        results = predict_text_sentiment(text)
        return jsonify({'sentiment': results['sentiment']})
    
    except Exception as e:
        return jsonify({'error': str(e)})

color_classes = ['text-success', 'text-danger', 'text-primary', 'text-info', 'text-warning']

@dashboards_bp.route("/dashboard", methods=["GET"])
@login_required
def home():
    latest_tweets = get_latest_tweets()
    tweets_and_colors = zip(latest_tweets, color_classes)
    return render_template("dashboard/pages/index.html", 
                           tweets_statistics = get_tweet_count_dictionary(),
                           tweets_and_colors = tweets_and_colors
                           )


class PaginationForm(FlaskForm):
    page = IntegerField('Page', default=1)

@dashboards_bp.route("/tweets", methods=["GET"])
@login_required
def show_tweets_page():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    tweets = Tweet.query.paginate(page, per_page, False)
    pagination = Pagination(page = page, per_page = per_page, total = tweets.total, query='', items='')
    return render_template("dashboard/pages/show_tweets.html", 
                           tweets_statistics = get_tweet_count_dictionary(),
                           tweets = tweets.items, pagination = pagination, 
                           )


@dashboards_bp.route("/feedback", methods=["GET"])
@login_required
def show_feedback_page():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    feedback_results = Feedback.query.paginate(page, per_page, False)
    pagination = Pagination(page = page, per_page = per_page, total = feedback_results.total, query='', items='')
    return render_template("dashboard/pages/feedback.html", 
                           feedback_results = feedback_results.items, pagination = pagination)


@dashboards_bp.route("/save-feedback", methods=["POST"])
@login_required
def save_feedback():
    name = request.form.get('name')
    phone = request.form.get('phone')
    content = request.form.get('content')

    new_feedback = Feedback(name=name, phone=phone, content=content)
    db.session.add(new_feedback)
    db.session.commit()

    flash("New feedback added.", "success")
    return redirect('/feedback')


class TweetAnalyzer:
    def __init__(self):
        # Initialize anything you need here
        pass

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, text):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        #call function to predict sentiment of passed tweet
        results = predict_text_sentiment(text)
        # return results
        return results['sentiment']
    

    def get_tweets(self, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # Load your tweets dataset
        tweets_dataset = pd.read_csv(url)

        # Filter tweets based on query (if needed)
        filtered_tweets = tweets_dataset.head(count)

        # Initialize an empty list to store parsed tweets
        tweets = []

        # Parsing filtered tweets one by one
        #for tweet in filtered_tweets:
        for index, tweet in filtered_tweets.iterrows():
            parsed_tweet = {}
            
             # Saving text of tweet
            parsed_tweet['tweet'] = tweet['tweet']
            # Saving name of tweet owner
            parsed_tweet['name'] = tweet['name']
            # Saving username of tweet owner
            parsed_tweet['username'] = tweet['username']
             # Saving username of tweet owner
            parsed_tweet['tweet_created_at'] = tweet['created_at']
            # Saving sentiment of tweet
            parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet['tweet'])


            store_tweet(tweet = parsed_tweet['tweet'],
                        name = parsed_tweet['name'],
                        username = parsed_tweet['username'],
                        tweet_created_at = convert_utc_time_to_local_time(parsed_tweet['tweet_created_at']),
                        sentiment = parsed_tweet['sentiment'])

            # Appending parsed tweet to tweets list
            tweets.append(parsed_tweet)

        # Return parsed tweets
        return tweets

def fetch_tweets():
    api = TweetAnalyzer()
    # calling function to get tweets
    tweets = api.get_tweets(count = 10000)
    
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} % \
            ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)))
    
    return False
 

def store_tweet(tweet, name, username, tweet_created_at ,sentiment):
     new_tweet = Tweet(tweet = tweet, name = name, username = username, tweet_created_at = tweet_created_at, sentiment = sentiment)
     db.session.add(new_tweet)
     db.session.commit()

def get_tweet_count_dictionary():
    positive_tweets = Tweet.query.filter_by(sentiment='positive').count()
    negative_tweets = Tweet.query.filter_by(sentiment='negative').count()
    neutral_tweets = Tweet.query.filter_by(sentiment='neutral').count()
    all_tweets = Tweet.query.count()
    return {
    "positive_tweets": positive_tweets,
    "negative_tweets": negative_tweets,
    "neutral_tweets": neutral_tweets,
    "all_tweets": all_tweets
    }

def get_latest_tweets(count = 10):
    latest_tweets = Tweet.query.order_by(Tweet.tweet_created_at.desc()).limit(count).all()
    return latest_tweets



def convert_utc_time_to_local_time(utc_timestamp):
    # Define the UTC timestamp
    utc_timestamp = datetime.strptime("2023-02-28 00:36:05", "%Y-%m-%d %H:%M:%S")

    utc_timestamp = pytz.utc.localize(utc_timestamp)
    # Create a time zone object for Africa/Kampala
    kampala_tz = pytz.timezone('Africa/Kampala')
    # Convert the UTC timestamp to the Kampala time zone
    kampala_time = utc_timestamp.replace(tzinfo=pytz.utc).astimezone(kampala_tz)
    return kampala_time



@dashboards_bp.route("/refresh", methods=["GET"])
@login_required
def load_tweets():
    db.session.query(Tweet).delete()
    db.session.commit()
    fetch_tweets()
    flash("New tweets fetched.", "success")
    return redirect(url_for("dashboards.home"))






