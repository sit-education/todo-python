from app import db

class users(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    login = db.Column(db.String(200))
    password = db.Column(db.String(200))
    email = db.Column(db.String(200))
    firstName = db.Column(db.String(200))
    lastName = db.Column(db.String(200))
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


#class tokens(db.Model):
	#token = db.Column(db.String(200))
	#id = db.Column('id', db.Integer)

	#def __init__(self,token,id):
		#self.token = token
		#self.id = id

	#def __repr__(self):
		#return str(('%s'%self.token,'%s'%self.id))