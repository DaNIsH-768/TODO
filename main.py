from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from verification import verify_username, verify_password
import secrets

"""
A simple Flask-based Todo application with SQLite database integration.

Modules:
     - flask: Web framework for Python.
     - flask_sqlalchemy: SQLAlchemy integration for Flask.
     - datetime: For handling date and time.

Classes:
     Todo(db.Model):
          Represents an active Todo item.
          Attributes:
               id (int): Primary key.
               title (str): Title of the todo item (required).
               description (str): Description of the todo item (required).
               date_created (date): Date when the todo was created (defaults to current date).
          Methods:
               __repr__: Returns a string representation of the Todo instance.

     Completed(db.Model):
          Represents a completed Todo item (stored in a separate database).
          Attributes:
               id (int): Primary key.
               title (str): Title of the completed todo item (required).
               description (str): Description of the completed todo item (required).
               date_created (date): Date when the todo was created (defaults to current date).
          Methods:
               __repr__: Returns a string representation of the Completed instance.

Routes:
     '/' [GET]:
          Renders the home page displaying all active and completed todo items.
     '/' [POST]:
          Handles submission of new todo items via form.
          Validates input and adds new item to the database.
     '/complete/<int:id>' [GET]:
          Marks a todo item as completed (moves it to the completed database).
     '/delete/<int:id>' [GET]:
          Deletes the active todo item with the specified ID.
     '/delete_comp/<int:id>' [GET]:
          Deletes the completed todo item with the specified ID.
     '/clear_completed' [GET]:
          Deletes all completed todo items.

Application Entry Point:
     - Creates database tables if they do not exist.
     - Runs the Flask development server in debug mode.
"""

def authenticate_user(username, password):
     ...

app = Flask(__name__)
app.secret_key = secrets.token_hex()
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  # All todos database
app.config['SQLALCHEMY_BINDS'] = {
    'completed': 'sqlite:///completed_db.sqlite3',  # Completed todos database
    'users': 'sqlite:///users_db.sqlite3'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(30), nullable=False)
     password_hash = db.Column(db.String(), nullable=False)

     def __repr__(self):
        return f"<ID {self.id} - username {self.username}>"

class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Date, default=datetime.utcnow().date)

    def __repr__(self):
        return f"<Todo {self.id} - {self.title}>"
    
class Completed(db.Model):
     __bind_key__ = 'completed'

     id = db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String(100), nullable=False)
     description = db.Column(db.Text, nullable=False)
     date_created = db.Column(db.Date, default=datetime.utcnow().date)

     def __repr__(self):
        return f"<Todo {self.id} - {self.title}>"

@app.route('/')
def hello():
     todos = Todo.query.all()
     completed = Completed.query.all()
     return render_template('home.html', todos=todos, completed=completed)

@app.route('/login')
def login():
     return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          confirm_password = request.form['confirm_password']

          user = User.query.filter_by(username=username).first()

          if user:
               flash('User already exists.', 'error')
          elif not verify_username(username):
               flash('Invalid username.', 'error')
          elif not verify_password(password):
               flash('Invalid password.', 'error')
          elif password != confirm_password:
               flash('Passwords do not match.', 'error')
          else:
               password_hash = bcrypt.generate_password_hash(password)
               user = User(username=username, password_hash=password_hash)
               db.session.add(user)
               db.session.commit()
               flash('User added successfully.', 'success')
               return redirect(url_for('login'))

     return render_template('signup.html')

@app.route('/', methods=['POST'])
def handle_submit():
     try:
          title = request.form['title']
          desc = request.form['description']
          if not title or not desc:
               return "Title and description are required.", 400

          todo = Todo(title=title, description=desc)
          db.session.add(todo)
          db.session.commit()
          flash('Added successfully')
          return redirect('/')
     except Exception as e:
          db.session.rollback()
          return f"An error occurred: {str(e)}", 500

@app.route('/complete/<int:id>')
def handle_complete(id):
     todo = Todo.query.get(id)
     completed = Completed(title=todo.title, description = todo.description)
     db.session.add(completed)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/delete/<int:id>')
def handle_delete(id):
     todo = Todo.query.get(id)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/delete_comp/<int:id>')
def handle_delete_comp(id):
     todo = Completed.query.get(id)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/clear_completed')
def handle_clear_completed():
     todos = Completed.query.delete()
     db.session.commit()
     return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)