from flask import render_template, request, redirect, url_for, session, flash, get_flashed_messages 
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
import secrets
from tables import User

#Initializing Logging
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(filename='app.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG,)


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
            logger.exception("Failed to send Email")
            return "Something went wrong", 500


#Route registration
def register_routes(app, db_session):
      #Setting up email 
      app.config['MAIL_SERVER'] = 'smtp.gmail.com'
      app.config['MAIL_PORT'] = 587
      app.config['MAIL_USE_TLS'] = True
      app.config['MAIL_USE_SSL'] = False
      app.config['MAIL_USERNAME'] = 'hera.liepniece@gmail.com'
      app.config['MAIL_PASSWORD'] = 'tdtq zpwq dpdb ywex'
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

                  if not user_email:
                        logger.warning("Registration attempt without inputting email")
                        return "Please provide your email", 400
                  
                  session['email'] = user_email
                  otp = generate_OTP()
                  logger.debug(f"OTP generated for {user_email}: {otp}")

                  otp_email(user_email,otp)
                  logger.info(f"OTP was sent to {user_email}")
                  
                  return redirect(url_for('check_otp'))
            return render_template('registration.html')   


      #check if the otp entered is valid
      @app.route('/otp_check', methods=['GET', 'POST'])
      def check_otp():
            if request.method =="POST":
                  user_otp = request.form.get('otp')
                  if user_otp == session.get('otp'):
                        logger.info(f"OTP succesfully verified for user: {session.get('email')}")
                        return redirect(url_for('create_password'))
                  else:
                        logger.warning("User Entered Incorrect OTP")
                        return 'Incorrect OTP. Please Try Again.'
            return render_template('otp_check.html')


      #new page that allows users to set up a new password:
      @app.route('/new_password', methods=[ 'GET', 'POST'])
      def create_password():
            if request.method == 'POST':
                  new_password = request.form.get('new_password')
                  username = session.get('email')
                  role = session.get('role_select')

                  
                  upper = lower = digit = False
                  if 8 <= len(new_password) <= 20:
                        for char in new_password:
                              if char.isdigit():
                                    digit = True
                              elif char.isupper():
                                    upper = True
                              elif char.islower():
                                    lower = True
                  else:
                       flash('Password must be between 8 and 20 characters.', 'error')
                       logger.warning("Password length requirement not met: %s", username)
                       return redirect(url_for('create_password'))
                  
                  if not (upper and lower and digit):
                        flash('Password must contain at least one uppercase letter, one lowercase letter, and one number.', 'error')
                        logger.warning("Password complexity requirement not met: %s", username)
                        return redirect(url_for('create_password'))
                  
                  exists = db_session.query(User).filter_by(username=username).first()
                  if exists:
                        flash('Username already exists! Please try again.', 'error')
                        logger.error("Attempted registration with existing username: %s", username)
                        return redirect(url_for('create_password'))


                  #if successfull
                  flash('Your password has successfully been set. Please log in.', 'success')
                  logger.info("New user created: %s with role %s", username, role)

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
                        logger.info("User selected role: Team Member")
                        return redirect(url_for('tm_login'))
                  
                  elif role_selection == 'project_manager':
                        logger.info("User selected role: Project Manager")
                        return redirect(url_for('pm_login'))
            return render_template('role_select.html')


      
      @app.route('/tm_login', methods=['GET', 'POST'])
      def tm_login():
            if request.method == 'POST':
                  username = request.form.get('username')
                  password = request.form.get('password')

                  user = db_session.query(User).filter_by(username=username, role = 'team_member').first()
            
                  if user and bcrypt.check_password_hash(user.password, password):
                        logger.info(f"Team member '{username}' logged in successfully.")
                        return redirect(url_for('tm_dashboard'))
                  else:
                        logger.error("Wrong Username or Password Entered")
                        return 'Invalid username or password. Please try again.'
            return render_template('tm_login.html')    

      @app.route('/pm_login', methods=['GET','POST'])
      def pm_login():
            if request.method == 'POST':
                  username = request.form.get('username')
                  password = request.form.get('password')


                  if username == "projectmanager" and password == "eyespy":
                        logger.info(f"Project manager logged in successfully.")
                        return redirect(url_for('pm_dashboard'))
                  else:
                        logger.error("Wrong Username or Password Entered")
                        return 'Invalid username or password. Please try again.'
            return render_template('pm_login.html')
      
      @app.route('/pm_dashboard')
      def pm_dashboard():
            if request.method == 'POST':
                  title = request.form.get('task')
                  assigned_to = request.form.get('assigned_to')

                  user = db_session.query(User).get(int(assigned_to))

                  if user:
                        new_task = Task(title=title,
                        status="Not Started",  #Default status
                        assigned_to=user.id)
                        db_session.add(new_task)
                        db_session.commit()

                  #redirect back to the pm dashboard
                  return redirect(url_for('pm_dashboard'))

            team_members = db_session.query(User).filter_by(role='team_member').all()
            tasks = db_session.query(Task).all()
    
            return render_template('pm_dashboard.html', team_members=team_members, tasks=tasks)

      @app.route('/dashboard')
      def tm_dashboard():
            if 'user_id' not in session:
                  return redirect(url_for('tm_login'))

            user = db_session.query(User).get(session['user_id'])
            tasks = db_session.query(Task).filter_by(assigned_to=user.id).all()
            return render_template('tm_dashboard.html', user=user, tasks=tasks)
      
      @app.route('/update_task_status/<int:task_id>', methods=['POST'])
      def update_task_status(task_id):
            new_status = request.form.get('status')
    
            task = db_session.query(Task).get(task_id)
            if task:
                  task.status = new_status
                  db_session.commit()

            return redirect(url_for('tm_dashboard'))
      
      @app.route('/remove_user/<int:user_id>', methods=['POST'])
      def remove_user(user_id):
            user = db_session.query(User).get(user_id)
            if user:
                  db_session.delete(user)
                  db_session.commit()
            else:
                  print('User not found.', 'error')
            return redirect(url_for('pm_dashboard'))

      
      @app.route('/add_user', methods=['POST'])
      def add_user():
            username = request.form['username']
            role = 'team_member'
            password = request.form['password']

            upper = lower = digit = False
            if 8 <= len(password) <= 20:
                  for char in password:
                        if char.isdigit():
                              digit = True
                        elif char.isupper():
                              upper = True
                        elif char.islower():
                              lower = True
            else:
                  print('Password must be between 8 and 20 characters', 'error')
                  return redirect(url_for('pm_dashboard'))
            
            if not (upper and lower and digit):
                  print('Password must contain at least one uppercase letter, one lowercase letter, and one number.', 'error')
                  return redirect(url_for('pm_dashboard'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            existing_user = db_session.query(User).filter_by(username=username).first()
            if existing_user:
                  print('User with this username already exists.', 'error')
                  return redirect(url_for('pm_dashboard'))

            new_user = User(username=username, role=role, password=hashed_password)
            db_session.add(new_user)
            db_session.commit()

            return redirect(url_for('pm_dashboard'))
      
      







      



      @app.errorhandler(Exception)
      def handle_exception(e):
            logger.exception("Unhandled exception occurred")
            return "Something went Wrong", 500


