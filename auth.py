from flask import render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
import secrets
from tables import User


#Flask Set Up for Auth
bcrypt = Bcrypt()
mail = Mail()

#Generates OTP
def generate_OTP():
      otp = secrets.randbelow(900000) 
      session['otp'] = str(otp)
      return otp


#Sends OTP email     
def otp_email(user_email, otp):
      try:
        msg = Message("One-Time Password for Registration", recipients=[user_email])
        msg.body =f"Your one-time password is: {otp}\n This password will expire in 10 minutes."
        mail.send(msg)
      except Exception as e:
            print(f"SMTP ERROR: {e}")
            raise


#Route registration
def register_routes(app, db_session):
      #Setting up email 
      app.config['MAIL_SERVER'] = 'smtp.gmail.com'
      app.config['MAIL_PORT'] = 587
      app.config['MAIL_USE_TLS'] = True
      app.config['MAIL_USE_SSL'] = False
      app.config['MAIL_USERNAME'] = 'hera.liepniece@gmail.com'
      app.config['MAIL_PASSWORD'] = 'jlch tsib qadb nf'
      app.config['MAIL_DEFAULT_SENDER'] = 'hera.liepniece@gmail.com'
      
      mail.init_app(app)
      bcrypt.init_app(app)


      #Home route for login form
      @app.route('/')
      def home():
            return render_template('role_select.html')   

      #User Registration with OTP
      @app.route('/registration', methods=['GET', 'POST'])
      def registration():
            if request.method == 'POST':
                  user_email= request.form.get('email')
                  session['email'] = user_email
                  otp = generate_OTP()
                  otp_email(user_email,otp)
                  return redirect(url_for('otp_check'))
            return render_template('registration.html')   


      #check if the otp entered is valid
      @app.route('/otp_check', methods=['GET', 'POST'])
      def check_otp():
            if request.methof =="POST":
                  user_otp = request.form.get('otp')
                  if user_otp == session.get('otp'):
                        return redirect(url_for('new_password'))
                  else:
                        return 'Incorrect OTP. Please Try Again.'
            return render_template('otp_check.html')


      #new page that allows users to set up a new password:
      @app.route('/new_password', methods=[ 'GET', 'POST'])
      def create_password():
            if request.method == 'POST':
                  new_password = request.form.get('new_password')
                  username = session.get('email')
                  role = session.get('role_select')
                  hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
                  user = User(username=username, password = hashed_password, role = role)
                  db_session.add(user)
                  db_session.commit()
                  return redirect(url_for('tm_login'))
            

            return render_template('new_password.html')  


      @app.route('/role_select', methods=['GET', 'POST'])
      def role_select():
            if request.method == 'POST':
                  role_selection = request.form.get('role_select')
                  session['role_select'] = role_selection
                  if role_selection == 'team_member':
                        return redirect(url_for('tm_login'))
                  elif role_selection == 'project_manager':
                        return redirect(url_for('pm_login'))
            return render_template('role_select.html')



      #POST requests for login- checks for OTP instead of a password and redirects user to change it
      @app.route('/tm_login', methods=['GET', 'POST'])
      def tm_login():
            if request.method == 'POST':
                  username = request.form.get('username')
                  password = request.form.get('password')

                  user = db_session.query(User).filter_by(username=username, role = 'team_member').first()
            
                  if user and bcrypt.check_password_hash(user.password, password):
                        return f'Welcome Team Member! Login succesful.'
                  else:
                        return 'Invalid username or password.Please try again.'
            return render_template('tm_login.html')    

      @app.route('/pm_login', methods=['GET','POST'])
      def pm_login():
            if request.method == 'POST':
                  username = request.form.get('username')
                  password = request.form.get('password')



                  if username == "projectmanager" and password == "eyespy":
                        return f'Welcome Project Manager! Login succesful.'
                  else:
                        return 'Invalid username or password. Please try again.'
            return render_template('pm_login.html')



