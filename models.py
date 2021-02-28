from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# contains all usernames, passwords, and names of users
class User(db.Model):
	__tablename__ = "User"
	username = db.Column(db.String(256), primary_key=True)
	password = db.Column(db.String(256), nullable=False)
	name = db.Column(db.String(64), default="Anonymous")
	tasks = db.relationship('ToDo', backref='user', lazy=True)

# All todo items from all users are stored in this db
class ToDo(db.Model):
	__tablename__ = "ToDo"
	item_id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(1024), nullable=False)
	due_date = db.Column(db.String(10))
	is_complete = db.Column(db.Integer, default=0)
	username = db.Column(db.String(256), db.ForeignKey('User.username'), nullable=False)

	def __repr__(self):
		return '<Task %r>' % self.item_id
