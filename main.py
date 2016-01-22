"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify, Request
from flask import make_response
from functools import wraps
from flask_mail import Mail, Message
import re
import random
import string
import collections
from time import time
import os
from flask_sqlalchemy import SQLAlchemy
import MySQLdb
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
#app.config["SQLALCHEMY_ECHO"] = False
app.secret_key = "shahniggas"
app.config["SQLALCHEMY_DATABASE_URI"] ='mysql+gaerdbms:///users?instance=direct-subject-119713:database'
app.config["SQLALCHEMY_ECHO"] = False
app.config["JSON_SORT_KEYS"] = False

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'shahrustam98@gmail.com',
    MAIL_PASSWORD = '250585LEN'
    )


mail = Mail(app)

ADMINS = ['shahrustam98@gmail.com']

db = SQLAlchemy(app)

mysqls = MySQLdb.connect(unix_socket='/cloudsql/direct-subject-119713:database', db='users', user='root')

@app.route('/time')
def timess():
    response = make_response(redirect('/login'))  
    response.set_cookie('token',value='token', max_age=(int(time()+86400)))
    return response

def emcheck(email):
    check = re.search(r'[\w.-]+@[\w.-]+', email)
    return check

def gentoken():
    t=str(hex(int(time()*1000)))
    return t

class users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column('id', db.Integer, primary_key=True)
    login = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    firstName = db.Column(db.String(255))
    lastName = db.Column(db.String(255))
    emailVerified = db.Column(db.Integer)
    recoveryPass = db.Column(db.Integer)

    def __init__(self,login,password,email,firstName,lastName,emailVerified,recoveryPass):
        self.login = login
        self.password = password
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.emailVerified = emailVerified
        self.recoveryPass= recoveryPass

    def __repr__(self):
        return str(('%s'%self.login,'%s'%self.password,'%s'%self.email,'%s'%self.firstName,'%s'%self.lastName,'%s'%self.emailVerified,'%s'%self.recoveryPass))

class tokenss(db.Model):
    __tablename__ = 'tokens'
    __table_args__ = {'extend_existing': True}
    iddb= db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    id = db.Column(db.Integer)

    def __init__(self,token,id):
        self.token = token
        self.id = id

    def __repr__(self):
        return str(('%s'%self.token,'%s'%self.id))

class apitokenss(db.Model):
    __tablename__ = 'apiTokens'
    __table_args__ = {'extend_existing': True}
    ids= db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    id = db.Column(db.Integer)
    expiration = db.Column(db.String(255))

    def __init__(self,token,id,expiration):
        self.token = token
        self.id = id
        self.expiration= expiration

    def __repr__(self):
        return str(('%s'%self.token,'%s'%self.id,'%s'%self.expiration))

class verif(db.Model):
    __tablename__ = 'verif'
    __table_args__ = {'extend_existing': True}
    ids= db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(255))
    id = db.Column(db.String(255))

    def __init__(self,Code,id):
        self.Code = Code
        self.id = id

    def __repr__(self):
        return str(('%s'%self.Code,'%s'%self.id))

class recover(db.Model):
    __tablename__ = 'recovery'
    __table_args__ = {'extend_existing': True}
    id= db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __init__(self,Code,email):
        self.Code = Code
        self.email = email

    def __repr__(self):
        return str(('%s'%self.Code,'%s'%self.email))

def todoss(ids):
    class todos(db.Model):
        __tablename__ = 'todo%s'%ids
        __table_args__ = {'extend_existing': True}
        id = db.Column('id', db.Integer, primary_key=True)
        title = db.Column(db.String(255))
        description = db.Column(db.String(255))

        def __init__(self,title,description):
            self.title = title
            self.description = description

        def __repr__(self):
            return str(('%s'%self.title,'%s'%self.description))
    return todos

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        tokens = tokenss.query.all()
        if request.cookies:
            for x in tokens:
                if str(request.cookies['token']) == x.token:
                    if int(request.cookies['token_expired']) > int(time()):
                        return f(*args, **kwargs)
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('token', expires=0)
        resp.set_cookie('token_expired', expires=0)
        return resp
    return wrap

def login_already(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        tokens = tokenss.query.all()
        if request.cookies:
            for x in tokens:
                if str(request.cookies['token']) == x.token:
                    if int(request.cookies['token_expired']) > int(time()):
                        return redirect(url_for('items'))
        return f(*args, **kwargs)
    return wrap

@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if request.method == 'POST':
        oldmail=request.form["recemail"]
        if emcheck(oldmail) == None:
            flash('Invalid email!')
            return render_template('recovery.html')
        user = users.query.all()
        emails = []
        for i in user:
            emails.append(str(i.email))
        if emails.count(str(oldmail))==0:
            flash('This email not registered')
            return render_template('recovery.html')
        Code = gentoken()
        emailnew=['%s'%oldmail]
        msg = Message('Recovery password', sender = ADMINS[0], recipients = emailnew)
        msg.html =  '''
                    <h3>Please, <a href="http://direct-subject-119713.appspot.com/recovery/%s">click</a> to recovery your password</h3>
                
                    '''%(Code)
        mail.send(msg)
        user = users.query.filter_by(email='%s'%oldmail).first()
        user.recoveryPass = 0
        db.session.commit()
        #oldEmail = recover.query.filter_by(email='%s'%oldmail).first()
        #db.session.delete(oldEmail)
        #db.session.commit()
        newValues = recover(Code='%s'%Code, email='%s'%oldmail)
        db.session.add(newValues)
        db.session.commit()
        flash('Check your email for recover your password')
        return render_template('notification.html')
    return render_template('recovery.html')

@app.route('/recovery/<code>', methods=['GET', 'POST'])
def recoveryverif(code):
    codes = recover.query.all()
    if request.method == 'POST':
        newpass=request.form["newpass"]
        confpass=request.form["confpass"]
        if newpass!=confpass:
            flash('Passwords are not equal. Please try again')
            return render_template('newpass.html',nick=new)
        email = recover.query.filter_by(Code='%s'%code).first()
        user = users.query.filter_by(email='%s'%email.email).first()
        user.password = '%s'%newpass
        db.session.commit()
        db.session.delete(email)
        db.session.commit()
        flash('Your password has been changed')
        return render_template('notification.html')
    for x in codes:
        if str(code) == str(x.Code):
            nick = recover.query.filter_by(Code='%s'%code).first()
            nick = users.query.filter_by(email='%s'%nick.email).first()
            return render_template('newpass.html',nick=nick.firstName)
    return 'Invalid code'

@app.route('/signup', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        newemail=request.form["newemail"]
        newusername=request.form["newusername"]
        newfirstname=request.form["newfirstname"]
        newlastname=request.form["newlastname"]
        newuserpassword=request.form["newpassword"]
        confnewpass=request.form["confnewpass"]
        if emcheck(newemail) == None:
            flash('Invalid email!')
            return render_template('reg.html')
        if newuserpassword!=confnewpass:
            flash('Passwords are not equal. Please try again')
            return render_template('reg.html')
        user = users.query.all()
        for i in user:
            if (newemail.lower()==(i.email).lower()):
                flash('This email adress already exists')
                return render_template('reg.html')
            if (newusername.lower()==(i.login).lower()):
                flash('This login already exists')
                return render_template('reg.html')
        Code = gentoken()
        emailnew=['%s'%newemail]
        msg = Message('Confirm email address', sender = ADMINS[0], recipients = emailnew)
        msg.html =  '''
                    <h3>Please, <a href="http://direct-subject-119713.appspot.com/verification/%s">click</a> to confirm your registration</h3>
                
                    '''%(Code)
        mail.send(msg)
        newuser = users(login='%s'%newusername, password='%s'%newuserpassword, email='%s'%newemail, firstName='%s'%newfirstname, lastName='%s'%newlastname, emailVerified=0, recoveryPass=0)
        db.session.add(newuser)
        db.session.commit()
        IDD = (users.query.filter_by(email='%s'%newemail).first()).id
        vefiry = verif(Code='%s'%Code, id='%s'%IDD)
        db.session.add(vefiry)
        db.session.commit()
        tasks = mysqls.cursor()
        tasks.execute('CREATE TABLE todo%s(id INT NOT NULL AUTO_INCREMENT,title VARCHAR(255) ,description VARCHAR(255) ,PRIMARY KEY(id))'%IDD)
        mysqls.commit()
        flash('Check your email to continue registration')
        return render_template('notification.html')
    return render_template('reg.html')

@app.route('/verification/<cod>', methods=['GET', 'POST'])
def verify(cod):
    verify = verif.query.all()
    for m in verify:
        if cod == m.Code :
            user = users.query.filter_by(id='%s'%m.id).first()
            user.emailVerified = 1
            db.session.commit()
            delVerif = verif.query.filter_by(Code='%s'%m.Code).first()
            db.session.delete(delVerif)
            db.session.commit()
            flash('Registration was successful')
            return render_template('notification.html')
    return '''
                Invalid code
            '''

@app.route('/login', methods=['GET', 'POST'])
@login_already
def login():
    error = None
    count = users.query.all()
    if request.method == 'POST':
        usermd=request.form['username']
        passmd=request.form['password']
        for i in count:
            if (usermd.lower() == (i.login).lower()) and passmd.lower() == str(i.password).lower():
                if (i.emailVerified) == 0:
                    error = 'You did not confirm an email address.'
                    return render_template('login.html', error=error)
                token=gentoken()
                response = make_response(redirect('/items'))  
                response.set_cookie('token',value=token, max_age=(int(time()+86400)))
                response.set_cookie('token_expired',value=(str(int(time()+86400))),max_age=(int(time()+86400)))
                oldToken = tokenss.query.filter_by(id='%s'%(i.id)).first()
                if oldToken:
                    db.session.delete(oldToken)
                db.session.commit()
                newToken = tokenss(token='%s'%token,id='%s'%i.id)
                db.session.add(newToken)
                db.session.commit()
                return response
            else:
                error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/')
@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    if request.method == 'POST':
        if request.form['back']!= None:
            return redirect(url_for('items'))
    tasks = todoss(cur.id).query.all()
    return render_template('index.html', db=tasks, loginin = request.cookies['token'])

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    if request.method == 'POST':
        if request.form['add']== 'Add':
            title= request.form['title']
            descr= request.form['description']
            task = (todoss(cur.id))(title='%s'%title,description='%s'%descr)
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('items'))
    return render_template('add.html', loginin = request.cookies['token'])

@app.route('/itemdel/<nomb>', methods=['POST'])
@login_required
def itemdel(nomb):
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    task = (todoss(cur.id)).query.filter_by(id=nomb).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('items'))

@app.route('/item/<nomb>', methods=['GET', 'POST'])
@login_required
def item(nomb):
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    count = len((todoss(cur.id)).query.all()) + 1
    ids=[]
    tasks = todoss(cur.id).query.all()
    for k in tasks:
        ids.append(int(k.id))
    if ids.count(int(nomb))==0:
        return redirect(url_for('items'))
    edittod=(todoss(cur.id)).query.filter_by(id=nomb).first()
    return render_template('edit.html',loginin = request.cookies['token'], todo=edittod, nome=nomb)


@app.route('/apply/<ID>', methods=['GET', 'POST'])
@login_required
def apply(ID):
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    if request.method == 'POST':
        title= request.form['titleo']
        descr= request.form['descriptiono']
        task = todoss(cur.id).query.filter_by(id=ID).first()
        task.title = '%s'%title
        task.description = '%s'%descr
        db.session.commit()
    return redirect(url_for('items')) 

@app.route('/logout')
def logout():
    cur = tokenss.query.filter_by(token=(request.cookies['token'])).first()
    db.session.delete(cur)
    db.session.commit()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('token', expires=0)
    resp.set_cookie('token_expired', expires=0)
    return resp


def apilogin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        tokens = apitokenss.query.all()
        for x in tokens:
            if str(request.headers.get('Token-Key')) == x.token:
                if int(x.expiration) > int(time()):
                    return f(*args, **kwargs)
                massiv=collections.OrderedDict()
                massiv['error_key']="token_expired"
                massiv['error_message']='Token has expired.'
                errors=[]
                errors.append(massiv)
                return jsonify({'status':0, 'errors': errors }), 410
        massiv=collections.OrderedDict()
        massiv['error_key']="invalid_token"
        massiv['error_message']='Invalid token.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 401
    return wrap

def apilogin_already(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        tokens = apitokenss.query.all()
        for x in tokens:
            if str(request.headers.get('Token-Key')) == x.token:
                return f(*args, **kwargs)
        massiv=collections.OrderedDict()
        massiv['error_key']="invalid_token"
        massiv['error_message']='Invalid token.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 401
    return wrap

@app.route('/api/v1/restorePassword', methods=['POST'])
def apirecov():
    oldmail=request.json["email"]
    if emcheck(oldmail) == None:
        massiv=collections.OrderedDict()
        massiv['error_key']="invalid_email_format"
        massiv['error_message']='Invalid format of email'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    user = users.query.all()
    emails=[]
    for i in user:
        emails.append(str(i.email))
    if emails.count(str(oldmail))==0:
        massiv=collections.OrderedDict()
        massiv['error_key']="email_not_registered"
        massiv['error_message']='This email adress not registered'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    Code = gentoken()
    emailnew=['%s'%oldmail]
    msg = Message('Recovery password', sender = ADMINS[0], recipients = emailnew)
    msg.html =  '''
                 <h3>Please, <a href="http://ec2-52-11-248-121.us-west-2.compute.amazonaws.com/recovery/%s">click</a> to recovery your password</h3>
                
                '''%(Code)
    mail.send(msg)
    user = users.query.filter_by(email='%s'%oldmail).first()
    user.recoveryPass = 0
    db.session.commit()
    newValues = recover(Code='%s'%Code, email='%s'%oldmail)
    db.session.add(newValues)
    db.session.commit()
    return jsonify({'status':1, 'data': {} })

@app.route('/api/v1/signup', methods=['POST'])
def apisignup():
    newemail=request.json["email"]
    newusername=request.json["login"]
    newfirstname=request.json["firstName"]
    newlastname=request.json["lastName"]
    newuserpassword=request.json["password"]
    confnewpass=request.json["confPass"]
    if emcheck(newemail) == None:
        massiv=collections.OrderedDict()
        massiv['error_key']="invalid_email_format"
        massiv['error_message']='Invalid format of email'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    if newuserpassword!=confnewpass:
        massiv=collections.OrderedDict()
        massiv['error_key']="passwords_not_equal"
        massiv['error_message']='Passwords are not equal. Please try again'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    user = users.query.all()
    for i in user:
        if (newemail.lower()==(i.email).lower()):
            massiv=collections.OrderedDict()
            massiv['error_key']="email_already_exists"
            massiv['error_message']='This email adress already exists'
            errors=[]
            errors.append(massiv)
            return jsonify({'status':0, 'errors': errors }), 400
        if (newusername.lower()==(i.login).lower()):
            massiv=collections.OrderedDict()
            massiv['error_key']="login_already_exists"
            massiv['error_message']='This login already exists'
            errors=[]
            errors.append(massiv)
            return jsonify({'status':0, 'errors': errors }), 400
    Code = gentoken()
    emailnew=['%s'%newemail]
    msg = Message('Confirm email address', sender = ADMINS[0], recipients = emailnew)
    msg.html =  '''
                <h3>Please, <a href="http://ec2-52-11-248-121.us-west-2.compute.amazonaws.com/verification/%s">click</a> to confirm your registration</h3>
            
                '''%(Code)
    mail.send(msg)
    newuser = users(login='%s'%newusername, password='%s'%newuserpassword, email='%s'%newemail, firstName='%s'%newfirstname, lastName='%s'%newlastname, emailVerified=0, recoveryPass=0)
    db.session.add(newuser)
    db.session.commit()
    IDD = users.query.filter_by(email='%s'%newemail).first()
    vefiry = verif(Code='%s'%Code, id='%s'%IDD.id)
    db.session.add(vefiry)
    db.session.commit()
    task=MySQLdb.connect(unix_socket='/cloudsql/direct-subject-119713:database', db='users', user='root')
    tasks = task.cursor()
    tasks.execute('CREATE TABLE todo%s(id INT NOT NULL,title VARCHAR(255) ,description VARCHAR(255) ,PRIMARY KEY(id))'%IDD.id)
    task.commit()
    token=gentoken()
    token_expired= str(int(time()+86400))
    newToken = apitokenss(token='%s'%token,id='%s'%IDD.id,expiration='%s'%token_expired)
    db.session.add(newToken)
    db.session.commit()
    tokenout=collections.OrderedDict()
    tokenout['user_id']=IDD.id
    tokenout['emailVerified']=IDD.emailVerified
    tokenout['tokenKey']=token
    tokenout['tokenExpired']=token_expired
    return jsonify({'status':1, 'data': tokenout })

@app.route('/api/v1/login', methods=['POST'])
def apilogin():
    userdb = users.query.all()
    loginmd=request.json['login']
    passmd=request.json['password']
    for i in userdb:
        if (loginmd.lower() == (i.login).lower()) and passmd.lower() == (i.password).lower():
            if i.emailVerified == 0:
                massiv=collections.OrderedDict()
                massiv['error_key']="unconfirmed_email"
                massiv['error_message']="You did not confirm an email address."
                errors=[]
                errors.append(massiv)
                return jsonify({'status':0, 'errors': errors }), 400
            token=gentoken()
            token_expired= str(int(time()+86400))
            oldToken = apitokenss.query.filter_by(id='%s'%(i.id)).first()
            if oldToken:
                db.session.delete(oldToken)
            db.session.commit()
            newToken = apitokenss(token='%s'%token,id='%s'%i.id,expiration='%s'%token_expired)
            db.session.add(newToken)
            db.session.commit()
            tokenout=collections.OrderedDict()
            tokenout['user_id']=i.id
            tokenout['emailVerified']=i.emailVerified
            tokenout['tokenKey']=token
            tokenout['tokenExpired']=token_expired
            return jsonify({'status':1, 'data': tokenout })
    massiv=collections.OrderedDict()
    massiv['error_key']="invalid_username_or_password"
    massiv['error_message']="Invalid username or password. Please try again."
    errors=[]
    errors.append(massiv)
    return jsonify({'status':0, 'errors': errors }), 400


@app.route('/api/v1/logout', methods=['POST'])
@apilogin_already
def apilogout():
    cur = apitokenss.query.filter_by(token=(request.headers.get('Token-Key'))).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    db.session.delete(cur)
    db.session.commit()
    return jsonify({'status':1, 'data':{}})  

@app.route('/api/v1/item', methods=['POST'])
@apilogin_required
def apiadd():
    title= request.json['title']
    if title == "":
        massiv=collections.OrderedDict()
        massiv['error_key']="title_should_be"
        massiv['error_message']='Title should be.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    descr= request.json['description']
    if descr == "":
        massiv=collections.OrderedDict()
        massiv['error_key']="description_should_be"
        massiv['error_message']='Description should be.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    cur = apitokenss.query.filter_by(token=(request.headers.get('Token-Key'))).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    task = (todoss(cur.id))(title='%s'%title,description='%s'%descr)
    db.session.add(task)
    db.session.commit()
    return jsonify({'status':1, 'data': {}})


@app.route('/api/v1/items', methods=['GET'])
@apilogin_required
def apiitems():
    cur = apitokenss.query.filter_by(token=(request.headers.get('Token-Key'))).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    massiv = []
    tasks = (todoss(cur.id)).query.all()
    for x in tasks:
        task = collections.OrderedDict()
        task['id']=x.id
        task['title']=x.title
        task['description']=x.description
        massiv.append(task)
    return jsonify({'status':1, 'data':{'todoData': massiv }})

@app.route('/api/v1/item/<numb>', methods=['Delete'])
@apilogin_required
def apiitemdelete(numb):
    cur = apitokenss.query.filter_by(token=(request.headers.get('Token-Key'))).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    ids=[]
    tasks = todoss(cur.id).query.all()
    for k in tasks:
        ids.append(int(k.id))
    if ids.count(int(numb))==0:
        massiv=collections.OrderedDict()
        massiv['error_key']="task_not_exist"
        massiv['error_message']='This task does not exist.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    task = (todoss(cur.id)).query.filter_by(id=numb).first()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'status':1, 'data': {}})


@app.route('/api/v1/item/<numb>', methods=['PUT'])
def apiitem(numb):
    cur = apitokenss.query.filter_by(token=(request.headers.get('Token-Key'))).first()
    tasks = mysqls.cursor()
    tasks.execute('ALTER TABLE todo%s AUTO_INCREMENT = 1'%(cur.id))
    mysqls.commit()
    ids=[]
    tasks = todoss(cur.id).query.all()
    for k in tasks:
        ids.append(int(k.id))
    if ids.count(int(numb))==0:
        massiv=collections.OrderedDict()
        massiv['error_key']="task_not_exist"
        massiv['error_message']='This task does not exist.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    title= request.json['title']
    if title == "":
        massiv=collections.OrderedDict()
        massiv['error_key']="title_should_be"
        massiv['error_message']='Title should be.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    descr= request.json['description']
    if descr == "":
        massiv=collections.OrderedDict()
        massiv['error_key']="description_should_be"
        massiv['error_message']='Description should be.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    task = todoss(cur.id).query.filter_by(id=numb).first()
    task.title = '%s'%title
    task.description = '%s'%descr
    db.session.commit()
    return jsonify({'status':1, 'data': {} })

@app.route('/api/v1/testSignup', methods=['POST'])
def testSignup():
    ids = (users.query.filter_by(email='shahrustam98@gmail.com').first()).id
    task=MySQLdb.connect(unix_socket='/cloudsql/direct-subject-119713:database', db='users', user='root')
    (task.cursor()).execute('Drop table todo%s'%ids)
    task.commit()
    token = apitokenss.query.filter_by(id='%s'%ids).first()
    db.session.delete(token)
    db.session.commit()
    verify = verif.query.filter_by(id='%s'%ids).first()
    db.session.delete(verify)
    db.session.commit()
    userdel = users.query.filter_by(email='shahrustam98@gmail.com').first()
    db.session.delete(userdel)
    db.session.commit()
    return jsonify({'status':1, 'data': {} })

@app.route('/api/v1/testRestore', methods=['POST'])
def testRestore():
    user = users.query.filter_by(email='goodshomess@gmail.com').first()
    user.recoveryPass = 0 
    db.session.commit()
    recov = recover.query.filter_by(email='goodshomess@gmail.com').first()
    db.session.delete(recov)
    db.session.commit()
    return jsonify({'status':1, 'data': {} })

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

