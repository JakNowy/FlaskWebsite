from datetime import datetime
from FlaskWebsite import db, login_manager
from flask_login import UserMixin
import pytz

def time():
    time = datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(microsecond=0)
    return time

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    comment = db.relationship('Comment', backref='author', lazy=True)
    email_confirmed = db.Column(db.Boolean, default=None)

    def __repr__(self):
        return f'User {self.username} {self.email}'

class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=time)

    def __repr__(self):
        return f'Comment {self.comment} {self.date}'