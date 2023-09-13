from datetime import datetime

from src import  db


class Tweet(db.Model):

    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String, unique=False, nullable=False)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    tweet_created_at =  db.Column(db.DateTime, nullable=False)
    sentiment = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, tweet, name, username, tweet_created_at, sentiment):
        self.tweet = tweet
        self.name = name
        self.username = username
        self.tweet_created_at = tweet_created_at
        self.sentiment = sentiment
        self.created_on = datetime.now()

    def __repr__(self):
        return f"<id {self.id}>"
    @property
    def formatted_created_at(self):
        return format_custom_date(self.tweet_created_at)
    
def format_custom_date(date_obj):
    day = date_obj.day
    day_suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
    
    formatted_date = date_obj.strftime(f"%d{day_suffix} %b, %Y")
    return formatted_date
    


class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    phone = db.Column(db.String, unique=False, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, phone, content):
        self.name = name
        self.phone = phone
        self.content = content
        self.created_on = datetime.now()

    def __repr__(self):
        return f"<id {self.id}>"
    @property
    def formatted_created_on(self):
        return format_custom_date(self.created_on)

    
