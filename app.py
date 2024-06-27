#All these libraries need to be installed on the system using the package manager, PIP on CMD. 
from msilib.schema import RadioButton
from flask import Flask,jsonify, render_template, flash, redirect, url_for, session, logging, request
#This is imported from the data.py in the same folder where firstpro.py exists.
#from data import posts
#MYSQL packages that operate with MySQL Database
from flask_mysqldb import MySQL, MySQLdb
#wtforms are built in forms that need to be installed on our system using pip and fileds need to included

from wtforms import Form, StringField, TextAreaField,PasswordField, validators, HiddenField,SelectField,RadioField
#passlib.hash is used for encrypting our password we want to use. 
from passlib.hash import sha256_crypt

import mysql.connector
#used for styling, are called as decorators as well
import numpy as np
import pickle
from functools import wraps
import os

from wtforms.fields.html5 import EmailField
#Sometimes, the versio of wtform will be different

#This is instance of flask, that accepts __name__ as a parameter
app = Flask(__name__)
app.secret_key = os.urandom(24)
#Secret key is used for the security purposes

#MySQL Configuration Codes
mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'placement'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Initialize the app for use with this MySQL class
mysql.init_app(app)

#Decorators used for checking login or logout
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Decorator, extracted from the Wraps class.

def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash('Unauthorized, You logged in', 'danger')
            return redirect(url_for('register'))
        else:
            return f(*args, *kwargs)
    return wrap

#Homepge route (a path to homepage)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def home1s():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/team')
def team():
    return render_template('team.html')

#A class for registration form 
class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=3, max=50)], render_kw={'autofocus': True})
    username = StringField('Username', [validators.length(min=3, max=25)])
    email = EmailField('Email', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)])
    password = PasswordField('Password', [validators.length(min=3)])

@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))

        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


#Login Form Class
class LoginForm(Form):    # Create Message Form
    username = StringField('Username', [validators.length(min=1)], render_kw={'autofocus': True})

# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        username = form.username.data
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('add_student'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('signin.html', form=form)

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('signin.html', form=form)
    return render_template('signin.html', form=form)

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    if result >0:
        return render_template('home.html', posts=posts)
    else:
        msg = 'No posts found'
        return render_template('home.html', msg=msg)
        cur.close()
        
#Dashboard
@app.route('/dashboard2')
@is_logged_in
def dashboard2():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM student")
    posts = cur.fetchall()
    if result >0:
        return render_template('viewdata.html', std=posts)
    else:
        msg = 'No posts found'
        return render_template('viewdata.html', msg=msg)
        cur.close()
        
#Dashboard
@app.route('/dashboard1')
@is_logged_in
def dashboard1():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    if result >0:
        return render_template('index.html', posts=posts)
    else:
        msg = 'No posts found'
        return render_template('index.html', msg=msg)
        cur.close()


model1 = pickle.load(open('scholar_model.pkl', 'rb'))
    
model = pickle.load(open('modelCampus.pkl', 'rb'))
#post form class
class PostForm1(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    gender = RadioField('Gender', choices=[('M','male'),('F','female')])
    puc = StringField('Puc Percentage', [validators.Length(min=2,max=3)])
    pucboard= RadioField('PU Board', choices=[('S','State'),('C','Central')])
    high=StringField('Highschool Percentage', [validators.Length(min=2,max=3)])
    highboard=RadioField('High School Board', choices=[('S','State'),('C','Central')])
    sub=RadioField('Subject', choices=[('A','Arts'),('C','Comm'),('SC','Science')])
    degree=StringField('Degree Percentage', [validators.Length(min=2,max=3)])
    workex=RadioField('Work Experience', choices=[('Y','Yes'),('N','No')])
    testscore=StringField('Test Percentage', [validators.Length(min=2,max=3)])
    spec=RadioField('Specialization', choices=[('C','CS'),('IT','IT')])
    Caste=RadioField('Caste', choices=[('C','Christian '),('I','Muslim'),('O','Other')])
    income=StringField('Annual Income')
    prevmark=StringField('Previous Year Percentage', [validators.Length(min=2,max=3)])




@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = []
    
    for x in request.form.values():
            
            
        if(x=='M'):
            x=1
        elif(x=='F'):
            x=0
        elif(x=='S'):
            x=1
        elif(x=='C'):
            x=0
        elif(x=='A'):
            x=0
        elif(x=='CM'):
            x=1
        elif(x=='SC'):
            x=2
        elif(x=='N'):
            x=0
        elif(x=='Y'):
            x=1
        elif(x=='CS'):
            x=1
        elif(x=='IT'):
            x=0
        try:
            int_features.append(int(x))
        except :
            print(x)
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM student")
    posts = cur.fetchall()
    name =request.form.get("fname")
    print(name)
    # print(posts)
    if(output==1):
       
        if result >0:
            return render_template('viewdata.html', prediction_text='Congratulations  ' + name + ' you will be placed ', std=posts,re=output)
        else:
            msg = 'No posts found'
            return render_template('dashboard.html', msg=msg)
    if(output==0):
        return render_template('viewdata.html', prediction_text='keep up the hardwork!  ' + name + ' Placement chances are low ',std=posts,re=output)
             
             
                               
@app.route('/predict_scholarship',methods=['POST'])
def predict_scholarship():
    '''
    For rendering results on HTML GUI
    '''
   
    
    int_features = []
    for x in request.form.values():
        if(x=='M'):
            x=0
        elif(x=='F'):
            x=1
        elif(x=='C'):
            x=1
        elif(x=='I'):
            x=2 
        elif(x=='O'):
            x=3
        
        try:
            int_features.append(int(x))
        except:
            print("asasa")
    final_features = [np.array(int_features)]
    prediction = model1.predict(final_features)

    output = round(prediction[0], 2)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM student")
    posts = cur.fetchall()
    name =request.form.get("fname")
    print(output)
    if(output==0):
        return render_template('viewdata.html', prediction_text='Sorry! Not Eligible for Scholarship ',re=output,std=posts)
    if(output==1):
        return render_template('viewdata.html', prediction_text='You are eligible for Post-Metric Scholarship',re=output,std=posts)
    if(output==2):
        return render_template('viewdata.html', prediction_text='You are eligible for Karnataka Minority  Scholarship',re=output,std=posts)                     
    if(output==3):
        return render_template('viewdata.html', prediction_text='You are eligible for Children of Beedi Worker Scholarship',re=output,std=posts)
    if(output==4):
            return render_template('viewdata.html', prediction_text='You are eligible for Children of Mica/Iron Scholarship',re=output,std=posts)
    if(output==5):
        return render_template('viewdata.html', prediction_text='You are eligible for Differently Able Scholarship',re=output,std=posts)
    if(output==6):
        return render_template('viewdata.html', prediction_text='You are eligible for Labour welfare commission Scholarship',re=output,std=posts)
    if(output==7):
        return render_template('viewdata.html', prediction_text='You are eligible for LIC Scholarship',re=output,std=posts)
    if(output==8):
        return render_template('viewdata.html', prediction_text='You are eligible for NTPC Scheme Scholarship',re=output,std=posts)
    if(output==9):
        return render_template('viewdata.html', prediction_text='You are eligible for VIT University Ignite Scholarship',re=output,std=posts)
    if(output==10):
        return render_template('viewdata.html', prediction_text='You are eligible for Indian Oil Corporation Scholarships Scholarship',re=output,std=posts)
    
        

        

@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    print('asas')
    return jsonify(output)

#Adding posts done by users here
@app.route('/add_student', methods=['GET', 'POST'])
@is_logged_in
def add_student():
    form = PostForm1(request.form)
    if request.method == 'POST' and form.validate():
        name=form.name.data
        gender=form.gender.data
        puc=form.puc.data
        pucboard=form.pucboard.data
        high=form.high.data
        highboard=form.highboard.data
        sub=form.sub.data
        degree=form.degree.data
        workex=form.workex.data
        testscore=form.testscore.data
        spec=form.spec.data
        Caste=form.Caste.data
        prevmark=form.prevmark.data
        income=form.income.data
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO `student`(`name`,`gender`,`puc`,`pucboard`, `high`, `highboard`, `sub`, `degree`, `workex`, `testscore`, `spec`,`Caste`,`prevmark`,`income`)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,gender,puc,pucboard,high,highboard,sub,degree,workex,testscore,spec,Caste,income,prevmark))
        
        mysql.connection.commit()

        cur.close()

        flash('post created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('adddata.html', form=form)









#post form class
class PostForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    body = TextAreaField('Body', [validators.Length(min=30)])

#Adding posts done by users here
@app.route('/add_post', methods=['GET', 'POST'])
@is_logged_in
def add_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO `posts`(`title`,`body`,`author`)  VALUES (%s,%s,%s)", (title,body,session['username']))
        
        mysql.connection.commit()

        cur.close()

        flash('post created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_post.html', form=form)

#This route will takes us a single post to be dispalyed on the screen. When a user clicks on any of the the link,
#a new page will be displayed. 
""" The post id will be passed here from the data.py file"""
@app.route('/post/<string:id>/')#for single post
def post(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts WHERE id = %s", [id])
    post = cur.fetchone()
    return render_template("post.html", post=post)


#All the posts or posts listed here
@app.route('/posts', methods=['GET', 'POST'])
def posts():
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM posts")
        posts = cur.fetchall()
        if result >0:
            return render_template('posts.html', posts=posts)
        else:
            msg = 'No posts found'
            return render_template('posts.html', msg=msg)
        cur.close()

"""
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password do not match")
    ])
    confirm = PasswordField('Confirm Password')
"""

#post forms for validating the form for the sake of updating the posts by the users.
#edit posts by the users themselves 
# Edit Article
@app.route('/edit_post/<string:id>', methods=['GET', 'POST'])
#@is_logged_in
def edit_post(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM posts WHERE id = %s", [id])

    post = cur.fetchone()
    cur.close()
    # Get form
    form = PostForm(request.form)

    # Populate article form fields
    form.title.data = post['title']
    form.body.data = post['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        # Execute
        cur.execute ("UPDATE posts SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Post Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_post.html', form=form)

#The users can delete their posts using this route
@app.route('/delete_post/<string:id>', methods=['POST'])
def delete_post(id): 
    cur = mysql.connection.cursor()
    cur.execute("DELETE from posts where id=%s", [id])
    mysql.connection.commit()
    cur.close()
    flash('post deleted', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():

        # Create cursor
    cur = mysql.connection.cursor()
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key="HeyIam"
    app.run(debug=True)


