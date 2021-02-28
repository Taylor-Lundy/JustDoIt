from flask import Flask, redirect, url_for, render_template, request, flash
from models import db, User, ToDo
import os.path

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

if (os.path.exists('book.sqlite') == False):
	db.create_all()


@app.route("/", methods=['GET', 'POST'])
def index():
	'''
	Home page
	this method also verifies the
	login information provided by
	the login method
	'''
	global loggedIn
	global username

	if request.method == 'POST':
		uname = request.form['username']
		pword = request.form['pword']
		someUser = User.query.filter_by(username=uname).first()
		# first to check if this user even exists
		if someUser is None:
			flash('The username or password is invalid', 'failure')
			return redirect(url_for('login'))

		# now, check the password
		if pword != someUser.password:
			flash('The username or password is invalid', 'failure')
			return redirect(url_for('login'))

		# set loggedIn to true and set the username for this instance
		loggedIn = True
		username = uname
		flash('Signed in successfully!', 'success')

	return render_template("index.html")

@app.route("/tasks", methods=['GET', 'POST'])
def tasks():
	'''
	tasks page
	this is where tasks are displayed
	this method also takes the info from
	update and updates the task information
	'''
	global loggedIn
	global username
	global taskToUpdate

	someUser = User.query.filter_by(username=username).first()

	# if not logged in, send user to login page
	if loggedIn == False:
		return redirect(url_for("login"))

	# there are 2 cases in which we obtain a POST method in
	# task: 1) we are adding a new task to our ToDo list and
	# 2) we are updating a post with new info
	if request.method == 'POST':
		if taskToUpdate == None:
			description = request.form['description']
			due_date = request.form['due_date']
			new_item = ToDo(description=description, due_date=due_date, username=username)
			db.session.add(new_item)
			db.session.commit()
		else:
			update_description = request.form['update_description']
			update_due_date = request.form['update_due_date']
			if update_description != "":
				taskToUpdate.description = update_description
				db.session.commit()

			if update_due_date != "":
				taskToUpdate.due_date = update_due_date
			db.session.merge(taskToUpdate)
			db.session.commit()
			taskToUpdate = None

	tasks = ToDo.query.filter_by(username=username, is_complete=0).all()
	completed_tasks = ToDo.query.filter_by(username=username, is_complete=1).all()

	return render_template("tasks.html", name=someUser.name, ToDoList=tasks, CompletedList=completed_tasks)

@app.route("/add-task", methods=['GET', 'POST'])
def add_task():
	'''
	add-task page
	this is where tasks are added
	'''
	global loggedIn
	global username

	# if not logged in, send user to login page
	if loggedIn == False:
		return redirect(url_for("login"))
	return render_template("add_task.html")


@app.route("/complete/<int:item_id>")
def complete(item_id):
	'''
	The complete page
	Sets complete attribute for task to True (1)

	'''
	global loggedIn

	if loggedIn == False:
		return redirect(url_for("login"))

	task = ToDo.query.get_or_404(item_id)
	task.is_complete = 1
	db.session.merge(task)
	db.session.commit()
	return redirect(url_for("tasks"))


@app.route("/delete/<int:item_id>")
def delete(item_id):
	'''
	The delete page
	Deletes item from ToDo List
	'''
	global loggedIn
	if loggedIn == False:
		return redirect(url_for("login"))

	task = ToDo.query.get_or_404(item_id)

	db.session.delete(task)
	db.session.commit()
	return redirect(url_for("tasks"))

@app.route("/update/<int:item_id>")
def update(item_id):
	'''
	The update page
	Used to update the description
	of a task and/or the due date
	'''

	global taskToUpdate
	global loggedIn

	if loggedIn == False:
		return redirect(url_for('login'))

	taskToUpdate = ToDo.query.get_or_404(item_id)

	return render_template('update.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
	'''
	login page
	Also verifies that the register
	profile information is correct and that
	the username thereof isn't already taken
	'''
	global loggedIn
	global username

	# if alreday logged in, send user back to the home page
	if loggedIn == True:	
		return redirect(url_for("index"))

	if request.method == 'POST':
		# check if username is taken
		uname = request.form['username']
		pword = request.form['pword']
		pword2 = request.form['pword2']
		newname = request.form['name']
		someUser = User.query.filter_by(username=uname).first()
		if someUser is not None:
			message = "The username " + uname + " is already taken."
			flash(message, 'failure')
			return redirect(url_for("register"))
		
		# check if passwords are same
		if pword != pword2:
			flash('Password and Confirm Password must be the same', 'failure')
			return redirect(url_for("register"))

		# check if there is a name, if not, it will
		# default to 'Anonymous'
		if newname == None:
			newuser = User(username=uname, password=pword)
			db.session.add(newuser)
			db.session.commit()
		else:
			newuser = User(username=uname, password=pword, name=newname)
			db.session.add(newuser)
			db.session.commit()

		# now, set username for session and set loggedIn to True
		username = uname
		loggedIn = True
		flash("Account successfully created")
		return redirect(url_for("index"))
			

	return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
	'''
	register page
	used to make a new account
	'''
	global loggedIn

	# if logged In, redirect to homepage
	if loggedIn == True:
		return redirect(url_for("index"))

	return render_template("register.html")

if __name__ == "__main__":
	global loggedIn
	global username
	global taskToUpdate
	loggedIn = False
	username = None
	taskToUpdate = None
	app.run(port=3000)
