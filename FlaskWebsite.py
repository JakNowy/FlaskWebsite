from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, flash, redirect, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c07ee164909d05598b1840ac446e9cc2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'JakNowySolutions@gmail.com'
app.config['MAIL_PASSWORD'] = '!qwe123!'

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'positive'

from models import User, Comment
import forms


@app.route('/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('//<int:page>', methods=['GET', 'POST'])
@app.route('/home', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/home/<int:page>', methods=['GET', 'POST'])
def home(page):
    comments = Comment.query.order_by(Comment.date.desc()).paginate(per_page=2, page=page)
    form = forms.CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
    return render_template('index.html', comments=comments, form=form, page=page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.email_confirmed == True:
                if bcrypt.check_password_hash(user.password, form.password.data):

                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    # flash(f'Succesfully logged as {user.username}', category='positive')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
                else:
                    flash('Incorrect password.', category='negative')
            else: flash(f'This email has not been confirmed yet.{user.email_confirmed}', category='negative')
        else:
            flash('That user does not exist.', category='negative')
    return render_template('login.html', title = 'Log in', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            db.session.delete(user)
        user = User.query.filter_by(email=form.username.data).first()
        if user:
            db.session.delete(user)
        db.session.commit()
        user = User(username = form.username.data, email = form.email.data, password = pw)
        db.session.add(user)
        email = form.email.data
        token = serializer.dumps(email)
        msg = Message('Confirm your email', sender='jaknow394@gmail.com', recipients=[email])
        page_address = '127.0.0.1:5000'
        link = page_address + url_for('confirm_email', token=token)
        msg.body = f'Your confirmation link is: {link}'
        mail.send(msg)
        db.session.commit()

        flash(f'Account created for {form.username.data}. Please confirm your email address!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, max_age=120)
    except SignatureExpired:
        return '<h1>This token has expired!</h1>'
    else:
        user = User.query.filter_by(email=email).first()
        user.email_confirmed = True
        db.session.commit()
        flash('You can now log in!', category='positive')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/donate')
@login_required
def donate():
    pub_key = 'pk_test_dq5f53JDkyGYuaHRz1EjjuxW'
    secret_key = 'sk_test_6zQG2szKysCu7D3a3U4GiAQ4'
    stripe.api_key = secret_key
    return render_template('donate.html', title='Donate', pub_key=pub_key)

@app.route('/pay', methods=['POST'])
def pay():
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
        customer=customer,
        amount=999,
        currency='usd',
    )
    return redirect(url_for('home'))

