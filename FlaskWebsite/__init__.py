from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, flash, redirect
import FlaskWebsite.forms as forms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c07ee164909d05598b1840ac446e9cc2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@jn.pl' and form.password.data == '1234':
            flash(f'Succesfully logged as {form.username.data}', category='positive')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check the data.', category='negative')
    return render_template('login.html', title = 'Log in', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}. You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)