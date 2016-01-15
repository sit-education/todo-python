from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify, Request
from flask import make_response
from functools import wraps
from flask.ext.mail import Mail, Message
import sqlite3
import re
import random
import string
import collections
import datetime, time
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
app.secret_key = "shahniggas"
todo= sqlite3.connect("Todo.db")

global num
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


def emcheck(email):
    check = re.search(r'[\w.-]+@[\w.-]+', email)
    return check

def gentoken():
    t=str(hex(int(time.time()*1000)))
    return t


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        conn=sqlite3.connect("users.db")
        cur = conn.execute('select * from tokens')
        nom = ((conn.execute('select count(*) from tokens')).fetchall())[0][0]
        tokens = cur.fetchall()
        if request.cookies:
            for x in range(0,nom):
                if str(request.cookies['token']) == tokens[x][0]:
                    if int(request.cookies['token_expired']) > int(time.time()):
                        return f(*args, **kwargs)
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('token', expires=0)
        resp.set_cookie('token_expired', expires=0)
        return resp
    return wrap

def login_already(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        conn=sqlite3.connect("users.db")
        cur = conn.execute('select * from tokens')
        nom = ((conn.execute('select count(*) from tokens')).fetchall())[0][0]
        tokens = cur.fetchall()
        if request.cookies:
            for x in range(0,nom):
                if str(request.cookies['token']) == tokens[x][0]:
                    if int(request.cookies['token_expired']) > int(time.time()):
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
        oldusers = sqlite3.connect("users.db")
        cnt = ((oldusers.execute('select count(*) from users')).fetchall())[0][0]
        olduser = (oldusers.execute('select * from users')).fetchall()
        emails=[]
        for i in range(0,cnt):
            emails.append(str(olduser[i][3]))
        if emails.count(str(oldmail))==0:
            flash('This email not registered')
            return render_template('recovery.html')
        Code = gentoken()
        emailnew=['%s'%oldmail]
        msg = Message('Recovery password', sender = ADMINS[0], recipients = emailnew)
        msg.html =  '''
                    <h3>Please, <a href="http://ec2-52-11-248-121.us-west-2.compute.amazonaws.com/recovery/%s">click</a> to recovery your password</h3>
                
                    '''%(Code)
        mail.send(msg)
        oldusers.execute('update users set recoveryPass=\'0\' where email= \'%s\' '%(oldmail))
        oldusers.execute('Delete from recovery where email=\'%s\''%(oldmail))
        oldusers.execute('Insert into recovery (Code,email) values (\'%s\',\'%s\')' %(Code,oldmail))
        oldusers.commit()
        flash('Check your email for recover your password')
        return render_template('notification.html')
    return render_template('recovery.html')

@app.route('/recovery/<code>', methods=['GET', 'POST'])
def recoveryverif(code):
    recov= sqlite3.connect("users.db")
    rew= ((recov.execute('select count(*) from recovery')).fetchall())[0][0]
    cods=(recov.execute('select * from recovery')).fetchall()
    if request.method == 'POST':
        newpass=request.form["newpass"]
        confpass=request.form["confpass"]
        if newpass!=confpass:
            flash('Passwords are not equal. Please try again')
            return render_template('newpass.html',nick=new)
        users=sqlite3.connect('users.db')
        email= ((users.execute('select email from recovery where code =\'%s\' '%(code))).fetchall())[0][0]
        users.execute('Update users set password=\'%s\' where email=\'%s\' '%(newpass,email))
        users.execute('Delete from recovery where code=\'%s\''%(code))
        users.commit()
        flash('Your password has been changed')
        return render_template('notification.html')
    for x in range(0,rew):
        if code == cods[x][0]: 
            nickn=((recov.execute('select firstName from users where email=\'%s\''%(cods[x][1]))).fetchall())[0][0]
            return render_template('newpass.html',nick=nickn)
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
        dataBase = sqlite3.connect("users.db")
        cnt = ((dataBase.execute('select count(*) from users')).fetchall())[0][0]
        olduser = (dataBase.execute('select * from users')).fetchall()
        
        for i in range(0,cnt):
            if (newemail.lower()==olduser[i][3].lower()):
                flash('This email adress already exists')
                return render_template('reg.html')
        for i in range(0,cnt):
            if (newusername.lower()==olduser[i][1].lower()):
                flash('This login already exists')
                return render_template('reg.html')
        Code = gentoken()
        emailnew=['%s'%newemail]
        msg = Message('Confirm email address', sender = ADMINS[0], recipients = emailnew)
        msg.html =  '''
                    <h3>Please, <a href="http://ec2-52-11-248-121.us-west-2.compute.amazonaws.com/verification/%s">click</a> to confirm your registration</h3>
                
                    '''%(Code)
        mail.send(msg)
        dataBase.execute('Insert into users (login,password,email,firstName,lastName,emailVerified) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',0)' %(newusername,newuserpassword,newemail,newfirstname,newlastname))
        IDD = (dataBase.execute('select id from users where login=\'%s\'' %(newusername))).fetchall()
        dataBase.execute('Insert into verif (code,id) values (\'%s\',\'%s\') '%(Code,IDD[0][0]))
        dataBase.commit()
        task=sqlite3.connect("Todo.db")
        task.execute('CREATE TABLE \'todo%s\' (\'id\'INTEGER,\'title\' TEXT ,\'description\' TEXT ,PRIMARY KEY(id))'%(IDD[0][0]))
        task.commit()
        flash('Check your email to continue registration')
        return render_template('notification.html')
    return render_template('reg.html')

@app.route('/verification/<cod>', methods=['GET', 'POST'])
def verify(cod):
    verif= sqlite3.connect("users.db")
    rew= ((verif.execute('select count(*) from verif')).fetchall())[0][0]
    cods=(verif.execute('select * from verif')).fetchall()
    for m in range(0,rew):
        if cod == cods[m][0]:
            verif.execute('Update users set emailVerified=\'1\' where id=\'%s\' '%(cods[m][1]))
            verif.commit()
            verif.execute('Delete from verif where id=%s'%(cods[m][1]))
            verif.commit()
            flash('Registration was successful')
            return render_template('notification.html')
    return '''
                Invalid code
            '''






@app.route('/login', methods=['GET', 'POST'])
@login_already
def login():
    error = None
    conn=sqlite3.connect("users.db")
    cur = conn.execute('select * from users')
    kolvo = conn.execute('select count(*) from users')
    usersdb = cur.fetchall()
    kolvo = kolvo.fetchall()
    kolvo = kolvo[0][0]
    if request.method == 'POST':
        usermd=request.form['username']
        passmd=request.form['password']
        for i in range(0,kolvo):
            if (usermd.lower() == usersdb[i][1].lower()) and passmd.lower() == usersdb[i][2].lower():
                if usersdb[i][6] == 0:
                    error = 'You did not confirm an email address.'
                    return render_template('login.html', error=error)
                token=gentoken()
                response = make_response(redirect('/items'))  
                response.set_cookie('token',value=token, max_age=(int(time.time()+86400)))
                response.set_cookie('token_expired',value=(str(int(time.time()+86400))),max_age=(int(time.time()+86400)))
                conn.execute('Delete from tokens where id=\'%s\' '%(usersdb[i][0]))
                conn.commit()
                conn.execute('Insert into tokens (token,id) values (\'%s\',\'%s\')' %(token,usersdb[i][0]))
                conn.commit()
                return response
            else:
                error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/')
@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    cur = (((sqlite3.connect("users.db")).execute('select id from tokens where token=\'%s\' '%(request.cookies['token']))).fetchall())[0][0]
    if request.method == 'POST':
        if request.form['back']!= None:
            return redirect(url_for('items'))
        if request.form['delete']!= None:
            num=request.form['delete']
            todo.execute('Delete from todo%s where id=%s' %((cur),num))
            todo.commit()
    tasks = (todo.execute('select * from todo%s' %(cur))).fetchall()
    return render_template('index.html', db=tasks, loginin = request.cookies['token'])

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    cur = (((sqlite3.connect("users.db")).execute('select id from tokens where token=\'%s\' '%(request.cookies['token']))).fetchall())[0][0]
    if request.method == 'POST':
        if request.form['add']== 'Add':
            title= request.form['title']
            descr= request.form['description']
            todo.execute('Insert into todo%s (title,description) values (\'%s\',\'%s\')' %(cur,title,descr))
            todo.commit()
            return redirect(url_for('items'))
    return render_template('add.html', loginin = request.cookies['token'])



@app.route('/item/<nomb>', methods=['GET', 'POST'])
@login_required
def item(nomb):
    cur = (((sqlite3.connect("users.db")).execute('select id from tokens where token=\'%s\' '%(request.cookies['token']))).fetchall())[0][0]
    kolraz = ((todo.execute('select count(*) from todo%s' %(cur))).fetchall())[0][0]
    ids=[]
    tasks = (todo.execute('select * from todo%s' %(cur))).fetchall()
    for k in range(0,kolraz):
        ids.append(int(tasks[k][0]))
    if ids.count(int(nomb))==0:
        return redirect(url_for('items'))
    edittod=todo.execute('select * from todo%s where id=%s' %(cur,nomb))
    edittodo=edittod.fetchall()
    return render_template('edit.html',loginin = request.cookies['token'], todo=edittodo, nome=nomb)


@app.route('/apply/<ID>', methods=['GET', 'POST'])
@login_required
def apply(ID):
    cur = (((sqlite3.connect("users.db")).execute('select id from tokens where token=\'%s\' '%(request.cookies['token']))).fetchall())[0][0]
    if request.method == 'POST':
        titleo= request.form['titleo']
        descro= request.form['descriptiono']
        todo.execute('Update todo%s set title=\'%s\' where id=%s' %(cur,titleo,ID))
        todo.execute('Update todo%s set description=\'%s\' where id=%s' %(cur,descro,ID))
        todo.commit()
    return redirect(url_for('items')) 

@app.route('/logout')
def logout():
    conn=sqlite3.connect("users.db")
    conn.execute('Delete from tokens where token=\'%s\' '%(request.cookies['token']))
    conn.commit()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('token', expires=0)
    resp.set_cookie('token_expired', expires=0)
    return resp

def apilogin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        conn=sqlite3.connect("users.db")
        cur = conn.execute('select * from apitokens')
        nom = ((conn.execute('select count(*) from apitokens')).fetchall())[0][0]
        tokens = cur.fetchall()
        for x in range(0,nom):
            if str(request.headers.get('Token-Key')) == tokens[x][0]:
                if int(tokens[x][2]) > int(time.time()):
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
        conn=sqlite3.connect("users.db")
        cur = conn.execute('select * from apitokens')
        nom = ((conn.execute('select count(*) from apitokens')).fetchall())[0][0]
        tokens = cur.fetchall()
        for x in range(0,nom):
            if str(request.headers.get('Token-Key')) == tokens[x][0]:
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
    oldusers = sqlite3.connect("users.db")
    cnt = ((oldusers.execute('select count(*) from users')).fetchall())[0][0]
    olduser = (oldusers.execute('select * from users')).fetchall()
    emails=[]
    for i in range(0,cnt):
        emails.append(str(olduser[i][3]))
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
    oldusers.execute('update users set recoveryPass=\'0\' where email= \'%s\' '%(oldmail))
    oldusers.execute('Delete from recovery where email=\'%s\''%(oldmail))
    oldusers.commit()
    oldusers.execute('Insert into recovery (Code,email) values (\'%s\',\'%s\')' %(Code,oldmail))
    oldusers.commit()
    return jsonify({'status':1, 'data': {} })

@app.route('/api/v1/signup', methods=['POST'])
def apisignup():
    newemail=request.json["email"]
    newusername=request.json["login"]
    newfirstname=request.json["firstname"]
    newlastname=request.json["lastname"]
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
    dataBase = sqlite3.connect("users.db")
    cnt = ((dataBase.execute('select count(*) from users')).fetchall())[0][0]
    olduser = (dataBase.execute('select * from users')).fetchall()
    for i in range(0,cnt):
        if (newemail.lower()==olduser[i][3].lower()):
            massiv=collections.OrderedDict()
            massiv['error_key']="email_already_exists"
            massiv['error_message']='This email adress already exists'
            errors=[]
            errors.append(massiv)
            return jsonify({'status':0, 'errors': errors }), 400
    for i in range(0,cnt):
        if (newusername.lower()==olduser[i][1].lower()):
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
    dataBase.execute('Insert into users (login,password,email,firstName,lastName,emailVerified) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',0)' %(newusername,newuserpassword,newemail,newfirstname,newlastname))
    IDD = (dataBase.execute('select * from users where login=\'%s\'' %(newusername))).fetchall()
    dataBase.execute('Insert into verif (code,id) values (\'%s\',\'%s\') '%(Code,IDD[0][0]))
    dataBase.commit()
    token=gentoken()
    token_expired= str(int(time.time()+86400))
    dataBase.execute('Delete from apitokens where id=\'%s\' '%(IDD[0][0]))
    dataBase.commit()
    dataBase.execute('Insert into apitokens (token,id) values (\'%s\',\'%s\')' %(token,IDD[0][0]))
    dataBase.commit()
    tokenout=collections.OrderedDict()
    tokenout['user_id']=IDD[0][0]
    tokenout['emailVerified']=IDD[0][6]
    tokenout['tokenKey']=token
    tokenout['tokenExpired']=token_expired
    massiv=[]
    massiv.append(tokenout)
    return jsonify({'status':1, 'data': tokenout })

@app.route('/api/v1/login', methods=['POST'])
def apilogin():
    conn=sqlite3.connect("users.db")
    kolvo = ((conn.execute('select count(*) from users')).fetchall())[0][0]
    usersdb = (conn.execute('select * from users')).fetchall()
    loginmd=request.json['login']
    passmd=request.json['password']
    for i in range(0,kolvo):
        if (loginmd.lower() == usersdb[i][1].lower()) and passmd.lower() == usersdb[i][2].lower():
            if usersdb[i][6] == 0:
                massiv=collections.OrderedDict()
                massiv['error_key']="unconfirmed_email"
                massiv['error_message']="You did not confirm an email address."
                errors=[]
                errors.append(massiv)
                return jsonify({'status':0, 'errors': errors }), 400
            token=gentoken()
            token_expired= str(int(time.time()+86400))
            conn.execute('Delete from apitokens where id=\'%s\' '%(usersdb[i][0]))
            conn.commit()
            conn.execute('Insert into apitokens (token,id,expiration) values (\'%s\',\'%s\',\'%s\')' %(token,usersdb[i][0],token_expired))
            conn.commit()
            tokenout=collections.OrderedDict()
            tokenout['user_id']=usersdb[i][0]
            tokenout['emailVerified']=usersdb[i][6]
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
    conn=sqlite3.connect("users.db")
    conn.execute('Delete from apitokens where token=\'%s\' '%(request.headers.get('Token-Key')))
    conn.commit()
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
    cur = (((sqlite3.connect("users.db")).execute('select id from apitokens where token=\'%s\' '%(request.headers.get('Token-Key')))).fetchall())[0][0]
    todo.execute('Insert into todo%s (title,description) values (\'%s\',\'%s\')' %((cur),title,descr))
    todo.commit()
    massiv=[]
    return jsonify({'status':1, 'data': {}})


@app.route('/api/v1/items', methods=['GET'])
@apilogin_required
def apiitems():
    cur = (((sqlite3.connect("users.db")).execute('select id from apitokens where token=\'%s\' '%(request.headers.get('Token-Key')))).fetchall())[0][0]
    massiv = []
    counts= ((todo.execute('select count(*) from todo%s' %(cur))).fetchall())[0][0]
    itemss= (todo.execute('select * from todo%s' %(cur))).fetchall()
    tasks = collections.OrderedDict()
    for x in range(0,counts):
    	task = collections.OrderedDict()
        task['id']=itemss[x][0]
        task['title']=itemss[x][1]
        task['description']=itemss[x][2]
        massiv.append(task)
    return jsonify({'status':1, 'data':{'todoData': massiv }})

@app.route('/api/v1/item/<numb>', methods=['Delete'])
@apilogin_required
def apiitemdelete(numb):
    cur = (((sqlite3.connect("users.db")).execute('select id from apitokens where token=\'%s\' '%(request.headers.get('Token-Key')))).fetchall())[0][0]
    counts= ((todo.execute('select count(*) from todo%s' %(cur))).fetchall())[0][0]
    idss=[]
    tasks = (todo.execute('select * from todo%s' %(cur))).fetchall()
    for k in range(0,counts):
        idss.append(int(tasks[k][0]))
    if idss.count(int(numb))==0:
        massiv=collections.OrderedDict()
        massiv['error_key']="task_not_exist"
        massiv['error_message']='This task does not exist.'
        errors=[]
        errors.append(massiv)
        return jsonify({'status':0, 'errors': errors }), 400
    todo.execute('Delete from todo%s where id=%s' %((cur),numb))
    todo.commit()
    return jsonify({'status':1, 'data': {}})


@app.route('/api/v1/item/<numb>', methods=['PUT'])
def apiitem(numb):
    cur = (((sqlite3.connect("users.db")).execute('select id from apitokens where token=\'%s\' '%(request.headers.get('Token-Key')))).fetchall())[0][0]
    counts= ((todo.execute('select count(*) from todo%s' %(cur))).fetchall())[0][0]
    idss=[]
    tasks = (todo.execute('select * from todo%s' %(cur))).fetchall()
    for k in range(0,counts):
        idss.append(int(tasks[k][0]))
    if idss.count(int(numb))==0:
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
    todo.execute('Update todo%s set title=\'%s\' where id=%s' %((cur),title,numb))
    todo.execute('Update todo%s set description=\'%s\' where id=%s' %((cur),descr,numb))
    todo.commit()
    return jsonify({'status':1, 'data': {} })


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

if __name__ == '__main__':
    app.run()
