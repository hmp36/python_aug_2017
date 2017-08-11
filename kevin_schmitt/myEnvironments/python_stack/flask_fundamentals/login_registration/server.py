from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5, os, binascii
app = Flask(__name__)
app.secret_key = 'mykeysecret'
mysql = MySQLConnector(app,'user_reg')
@app.route('/')
def index():
    query = "SELECT * FROM users"                     # define your query
    users = mysql.query_db(query)  
    # print friends                                   # run query with query_db()
    return render_template('index.html', users=users) # pass data to our template
@app.route('/usersnew', methods=['POST'])
def create():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']
    
    is_valid = True
    if request.form['name'] == '':
        is_valid = False
        flash("Name cannot be blank")
    if request.form['email'] == '':
        is_valid = False
        flash("Email cannot be blank")
    if len(password) < 4:
        is_valid = False
        flash("Password must be atleast than 4 letters.")
    if password != password_confirmation:
        is_valid = False
        flash("Password must match Confirmation.")

    if is_valid == True:
        salt = binascii.b2a_hex(os.urandom(15))
        hashed_pw = md5.new(password + salt).hexdigest()
        query = 'INSERT INTO users (name, email, password, salt, created_at, updated_at) VALUES (:name, :email, :password, :salt, NOW(), NOW())'
        data = {
                'name': name,
                'email': email,
                'password': password,
                'salt': salt
                }
        mysql.query_db(query, data)
        return redirect('/success')
    else:
        return redirect('/')
@app.route('/success')
def success():
        return render_template('success.html')

@app.route('/sessions', methods=['POST'])
def login():
    query = 'select * from users where email = :email'
    data = { 'email': request.form['email'] }
    user = mysql.query_db(query, data)

    if len(user) == 0:
        flash('Invalid Credentials')
        return redirect('/')
    else:
        hashed_input_password = md5.new(request.form['password'] + user[0]['salt']).hexdigest()
        if hashed_input_password == user[0]['password']:
            return redirect('/success')
        else:
            flash('WRONG credentials')
            return redirect('/')



@app.route('/user/<users_id>')
def show(users_id):
    # Write query to select specific user by id. At every point where
    # we want to insert data, we write ":" and variable name.
    query = "SELECT * FROM users WHERE id = :specific_id"
    # Then define a dictionary with key that matches :variable_name in query.
    data = {'specific_id': users_id}
    # Run query with inserted data.
    friends = mysql.query_db(query, data)
    # Friends should be a list with a single object,
    # so we pass the value at [0] to our template under alias one_friend.
    return render_template('index.html', one_user=users[0])
app.run(debug=True)