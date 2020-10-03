from flask import url_for, redirect, render_template, request, session, Flask, flash
from flask_mysqldb import MySQL
import re
import MySQLdb
import time


app= Flask(__name__)
app.secret_key='5791628bb0b13ce0c676dfde280ba245'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pythonlogin'

app.debug = True
# Intialize MySQL
mysql = MySQL(app)


@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg =''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Username and Password donot matched'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/pythonlogin/forgot', methods=['GET', 'POST'])
def forget():
    msg=''
    #add functionlaity if the username matched then put the new password and change the entries of that user into the datbase as well
    #after forgot password redirect the user to the login page 
    if request.method== 'POST':
        email= request.form['email']
        new_password= request.form['new_password']
        confirm_password= request.form['confirm_password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        result=cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        if result and new_password==confirm_password:
            data= cursor.fetchone()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE accounts SET password=%s WHERE email = %s ', (confirm_password, email))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('login'))
        elif result and new_password!=confirm_password:
            msg='New Password not matched with the Confirmed Password'
        else:
            msg='No such account exists! Please Register'

    return render_template('new_profile.html',msg=msg)

@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account_2 = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Email already exists!'
        elif account_2:
            msg= 'Username already exists! Please use different one'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/post')
def post():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        msg='Create Your Posts'
        return render_template('post.html',account=account,msg=msg)
    return redirect(url_for('login'))

@app.route('/pythonlogin/post/createposts', methods=['GET', 'POST'])

def createposts():
    msg={}
    if 'loggedin' in session:
        if request.method== 'POST':
            posttitle= request.form['posttitle']
            post= request.form['post']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            result="INSERT INTO post(posttitle,post) VALUES(%s,%s)"
            values=(posttitle,post)
            cursor.execute(result,values)
            mysql.connection.commit()
            msg=posttitle,post
            return render_template('post.html',account=account, msg=msg)
    return redirect(url_for('post'))


if __name__=="__main__":
	app.run()