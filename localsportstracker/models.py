from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from localsportstracker import db, login_manager, app
from flask_login import UserMixin

'''
This sets up what our model classes will hold.
Sets up how our database will look.
'''

@login_manager.user_loader
def load_user(user_id):
    # get the user info from the database
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    # This holds all of the user attributes, the conditions for those attributes, and how it will be stored
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(
        db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Event', backref='author', lazy=True)
    # posts desribes the realtionship between User and Event

    def get_reset_token(self, expires_sec=1800):
        # This dumps the users encrypted id into the db
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        # This checks tries to retrieve a user's id
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        # This is the objects representation
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Event(db.Model):
    # This holds all of the user attributes, the conditions for those attributes, and how it will be stored
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # This connects the Event to the User

    def __repr__(self):
        # This is the objects representation
        return f"Event('{self.title}', '{self.date_posted}')"


'''
Stuff to add to Event Class
Location
type of sport
when it's happening
@Edward can you go ahead an delete this comment when you are done? -Steven
'''
