from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#Define tables
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)

    def __repr__(self):
        return '<User {}>'.format(self.username)   
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Define intermediate tables
stdntevents = db.Table('stdntevents',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('stdntid', db.Integer, db.ForeignKey('stdntinfo.id')),
    db.Column('eventid', db.Integer, db.ForeignKey('events.id')))

eventgrades = db.Table('eventgrades',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('gradeid', db.Integer, db.ForeignKey('grades.id')),
    db.Column('eventid', db.Integer, db.ForeignKey('events.id')))

class Stdntinfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oid = db.Column(db.String)
    firstname = db.Column(db.String)
    surname = db.Column(db.String)
    dob = db.Column(db.String)
    grade = db.Column(db.String)
    formclass = db.Column(db.String)
    events = db.relationship('Events', secondary=stdntevents, backref='participant')
    studentid = db.Column(db.String)

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(db.String)
    participants = db.relationship('Stdntinfo', secondary=stdntevents, backref='event')
    grades = db.relationship('Grades', secondary=eventgrades, backref='event')

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.String)
    events = db.relationship('Events', secondary=eventgrades, backref='grade')

@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))