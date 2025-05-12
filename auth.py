import flask
from flask import Flask, request, render_template, session
import pyotp
import csv
import secrets
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt


# Database shall go here


# 
#Flask Set Up for Auth
app = Flask(__name__)
app.secret_key = '51275a136660d5b822051b9d4180bf51848855b61b6e79a2262c89d1998dc459'
bcrypt = Bcrypt(app)


#Setting up email 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hera.liepniece@gmail.com'
app.config['MAIL_PASSWORD'] = 'jlch tsib qadb nf'
app.config['MAIL_DEFAULT_SENDER'] = 'hera.liepniece@gmail.com'

mail = Mail(app)

def generate_OTP():
            otp = secrets.randbelow(900000) 
            session['otp'] = str(otp)
            return otp

            

def otp_email(user_email, otp):
       msg = Message("One-Time Password for Registration", recipients=[user_email])
       msg.body =f"Your one-time password is: {otp}\n This password will expire in 10 minutes."
       mail.send(msg)

#User Registration with OTP
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user_email= request.form.get('email')
        session['email'] = user_email
        otp = generate_OTP()
        otp_email(user_email,otp)
        return redirect(url_for('otp_check'))
    return render_template('register.html')   \
    

@app.route('/role_select', methods=['GET', 'POST'])
def role_select():
      if request.method == 'POST':
            role_selection = request.form.get('role_select')
            session['role_select'] = role_selection
            if role == 'team_member':
                  return redirect(url_for('tm_login'))
            elif role == 'project_manager':
                  return redirect(url_for('pm_login'))
      return render_template('role_select.html')

#Home route for login form
@app.route('/')
def home():
     return render_template('login.html')

#check if the otp entered is valid
@app.route('/otp_check', methods=['GET', 'POST'])
def check_otp():
      user_otp = request.form.get('otp')

      if user_otp == session.get('otp'):
            return redirect(url_for('new_password'))
      else:
            return 'Incorrect OTP. Please Try Again.'


#new page that allows users to set up a new password:
@app.route('/new_password', methods=[ 'GET', 'POST'])
def create_password():
         if request.method == 'POST':
            new_password = request.form.get('new_password')
            email = session.get('email')
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
            return redirect(url_for('tm_login'))

         return render_template('new_password.html')

# POST requests for login- checks for OTP instead of a password and redirects user to change it
@app.route('/tm_login', methods=['GET', 'POST'])
def tm_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            email = request.form.get('username')
            valid_password = request.form.get('password')
        
        if username == email and password == valid_password:
            return f'Welcome Team Member! Login succesful.'
        else:
                return 'Invalid username or password.Please try again.'
        

@app.route('/pm_login', methods=['GET','POST'])
def pm_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

        if username == projectmanager and password == eyespy:
            return f'Welcome Project Manager! Login succesful.'
        else:
                return 'Invalid username or password. Please try again.'
        

if __name__=='__main__':
     app.run(debug=True)


