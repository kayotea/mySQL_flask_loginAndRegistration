from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app,'login_reg')
app.secret_key = "dontyouknowthatyouretoxic"

@app.route('/')
def index():
    session['error_message'] = ""
    return render_template('index.html')

#login route
@app.route('/login', methods=['POST'])
def login():
    session['login_message'] = ""
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()

    query = "SELECT email, password FROM users"
    logins = mysql.query_db(query)
    print logins

    for person in logins:
        if person['email'] == email and person['password'] == password:
            query = "SELECT id FROM users WHERE users.email = :the_email"
            query_data = {'the_email': email}
            session['login'] = mysql.query_db(query, query_data)[0]['id']

            session['login_message'] = "login success!"
            return redirect('/success')

    session['login_message'] = "login failed"
    return redirect('/')

@app.route('/success')
def success():
    return render_template('success.html')

# registration form page
@app.route('/register')
def register():
    return render_template('register.html')

# take user input, validate
@app.route('/register/process', methods=['POST'])
def processRegistration():
    session['error_message'] = ""
    first = request.form['first']
    last = request.form['last']
    email = request.form['email']
    pw = request.form['pw']
    cpw = request.form['cpw']

    # if first name invalid, update error message
    if len(first) < 2 or not first.isalpha():
        session['error_message'] += "First name invalid. "
    # if last name invalid, update error message
    if len(first) < 2 or not last.isalpha():
        session['error_message'] += "Last name invalid. "
    #if email is invalid, update error message
    if not EMAIL_REGEX.match(email):
        session['error_message'] += "Email is not valid. "
    #if email is invalid, update error message
    if len(pw) < 8:
        session['error_message'] += "Password must be at least 8 characters. "
    #if email does not match confirmation email, update error message
    if pw != cpw:
        session['error_message'] += "Passwords do not match."

    # if there is an error message, redirect to register page
    if session['error_message']:
        return redirect('/register')
    # if there is no error message, add user into database
    else:
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
        data = {
            'first_name' : first,
            'last_name' : last,
            'email' : email,
            'password' : md5.new(pw).hexdigest()
        }
        mysql.query_db(query, data)
        # user is now registered and logged in
        query = "SELECT id FROM users WHERE users.email = :the_email"
        query_data = {'the_email': email}
        session['login'] = mysql.query_db(query, query_data)[0]['id']
        #return redirect('/show')
        return redirect('/success')

#used for debugging - directs to page that shows database contents
@app.route('/show')
def show():
    users = mysql.query_db("SELECT * FROM users")
    return render_template('show.html', users=users)

# delete user
@app.route('/delete/<user_id>')
def delete(user_id):
    query = "DELETE FROM users WHERE id = :id"
    data = {"id": user_id}
    mysql.query_db(query, data)
    return redirect('/show')

app.run(debug=True)