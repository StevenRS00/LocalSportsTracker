import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from localsportstracker import app, db, bcrypt, mail
from localsportstracker.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, PostForm
from localsportstracker.models import User, Event
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

'''
This file holds all of the routes that flask handles.
It takes care of some of the verifaction stuff as well.
'''

@app.route("/")
@app.route("/home")
def home():
    # This is the route to the main page that displays the posts.
    posts = Event.query.all()  # for new post
    return render_template('home.html', posts=posts)



@app.route("/about")
def about():
    # This is the route that takes the user to the about page.
    return render_template('about.html', title='About')


@app.route("/anouncements")
def anouncements():
    # This is the route that takes the user to see any announcements that are posted.
    return render_template('anouncements.html', title='Anouncements')


@app.route("/register", methods=['GET', 'POST'])
def register():
    # This route takes the user to the register page if the user aren't already signed in.
    if current_user.is_authenticated:
        # brings the user back to the main page after the user account has been created.
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # This adds the user to the database and encrypts the password.
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(
            f'Your account has been created {form.username.data}! You can now login', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # This route takes the user to the login page and prompts the user to sign in, if the user isn't already signed in.
    if current_user.is_authenticated:
        # It also brings the user back to the home page after a successful login.
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Checks if username and password match then returns them to home page if correct.
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    # This logs out the user and sends them to the home page.
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    # This stores a resized image of 125x125 and also creates a random name for it to be stored as.
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # This route takes you to the account page where it displays the user's account.
    # It also allows a user to uodate their info.
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        # This stroes the updated account info
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def send_reset_email(user):
    # This sends the user a token to their email to be able to change their password.
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # This page allows the user to enter their email attached to their account and request to change it.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        # sends an email with a link and token to change their password.
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been set with instuctions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # This route takes in a token and allows the user to reset their password if they want to.
    # If no token is given then it takes the person back to the reset request page.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # This is the form to reset the password and update the db.
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    # This is the form to create a new post
    form = PostForm()
    if form.validate_on_submit():
        post = Event(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        # updates db
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    # This loads a specific post.
    post = Event.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Event.query.get_or_404(post_id)
    if post.author != current_user:
        # If someone other than the author tries to update post it won't let them.
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # updates db.
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # This allows for a post to be deleted.
    post = Event.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
