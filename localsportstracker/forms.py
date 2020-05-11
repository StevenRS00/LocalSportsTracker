from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from localsportstracker.models import User

'''
This file takes care of what the forms will hold and how the input should be
taken in.
'''


class RegistrationForm(FlaskForm):
    # These variables that we use to create the Username, Email, and Passwords for the User's account.
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=8, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    # This is a button to create the user's account.

    def validate_username(self, username):
        # This functions makes sure that the username isn't already taken and then sets the username for the user.
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken already. Please choose another.')

    def validate_email(self, email):
        # This functions makes sure that the email hasn't been used before and then sets the email if it isn't already used.
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken already. Please choose another.')


class LoginForm(FlaskForm):
    # This shows the form for creating an account and has fields that you can type in.
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    # This shows the form for updating the account info of the user.
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=8, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        # This is another check for the username after the user is trying to update their account info
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken already. Please choose another.')

    def validate_email(self, email):
        # This is another check for the email after the user is trying to update their account info
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken already. Please choose another.')


class RequestResetForm(FlaskForm):
    # This class holds the field to hold which email a message will be sent to
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        # This makes sure that the email you entered actually has an account attached to it
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. Please create an account first.')


class ResetPasswordForm(FlaskForm):
    # This class holds the fields for a new password.
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')


class PostForm(FlaskForm):
    # This class shows the event form to be able to enter the event and post it.
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
