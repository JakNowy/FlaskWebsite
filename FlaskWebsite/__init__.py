from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, flash, redirect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c07ee164909d05598b1840ac446e9cc2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from FlaskWebsite.models import User, Comment
import FlaskWebsite.forms as forms


@app.route('/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('//<int:page>', methods=['GET', 'POST'])
@app.route('/home', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/home/<int:page>', methods=['GET', 'POST'])
def home(page):
    comments = Comment.query.order_by(Comment.date.desc()).paginate(per_page=3, page=page)
    form = forms.CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
    return render_template('index.html', comments=comments, form=form, page=page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                # flash(f'Succesfully logged as {user.username}', category='positive')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.', category='negative')
        else:
            flash('That user does not exist.', category='negative')
    return render_template('login.html', title = 'Log in', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}. You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
