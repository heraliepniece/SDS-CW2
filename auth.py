import flask
from flask import Flask, request, render_template

#Flask Set Up for Auth
app = Flask(__name__)

#Home route for login form
@app.route('/')
def home():
     return render_template('login.html')

# POST requests for login
@app.route('/login', methods=['POST'])
def login():
        username = request.form.get('username')
        password = request.form.get('password')

        valid_username = ""
        valid_password = ""
        
        if username == valid_username and password == valid_password:
            return f'Welcome! Login succesful.'
        else:
                return 'Invalid username or password.Please try again.'

if __name__ == '__main__':
    app.run(debug=True)

# GET requests for search
@app.route('/search', methods=['GET'])
def search():
    query= request.args.get('query')
# Perform search based on the query
    return f"Search results for: {query}"
# Responds to POST requests
if __name__ =='__main__':
      app.run(debug=True)



@app.route('/login',methods=['POST'])
def login():
     username = request.form.get('username')
     password = request.form.get('password')

   

if __name__=='__main__':
     app.run(debug=True)


