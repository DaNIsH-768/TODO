from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from verification import verify_username, verify_password
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
import secrets

"""
A Flask-based Todo application with user authentication and SQLite database integration.

Features:
     - User registration and login with password hashing (bcrypt).
     - User session management using Flask-Login.
     - Add, complete, and delete todo items.
     - Separate storage for active and completed todos.
     - Flash messages for user feedback.

Modules:
     - flask: Web framework for Python.
     - flask_sqlalchemy: SQLAlchemy ORM integration for Flask.
     - flask_bcrypt: Password hashing.
     - flask_login: User session management.
     - datetime: For handling date and time.
     - secrets: For generating secure secret keys.

Database Models:
     User(db.Model, UserMixin):
          - id (int): Primary key.
          - username (str): Unique username.
          - password_hash (str): Hashed password.

     Todo(db.Model):
          - id (int): Primary key.
          - title (str): Title of the todo item (required).
          - description (str): Description of the todo item (required).
          - date_created (date): Date when the todo was created (defaults to current date).

     Completed(db.Model):
          - id (int): Primary key.
          - title (str): Title of the completed todo item (required).
          - description (str): Description of the completed todo item (required).
          - date_created (date): Date when the todo was created (defaults to current date).

Routes:
     '/' [GET]:
          - Display all active and completed todo items (login required).
     '/' [POST]:
          - Add a new todo item (login required).
     '/login' [GET, POST]:
          - User login.
     '/signup' [GET, POST]:
          - User registration.
     '/complete/<int:id>' [GET]:
          - Mark a todo item as completed (login required).
     '/delete/<int:id>' [GET]:
          - Delete an active todo item (login required).
     '/delete_comp/<int:id>' [GET]:
          - Delete a completed todo item (login required).
     '/clear_completed' [GET]:
          - Delete all completed todo items (login required).
     '/logout' [GET]:
          - Log out the current user.

Application Entry Point:
     - Creates database tables if they do not exist.
     - Runs the Flask development server in debug mode.
"""

app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  # All todos database
app.config['SQLALCHEMY_BINDS'] = {
    'completed': 'sqlite:///completed_db.sqlite3',  # Completed todos database
    'users': 'sqlite:///users_db.sqlite3'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(30), nullable=False)
     password_hash = db.Column(db.String(), nullable=False)

     @staticmethod
     def get(user_id):
          return db.session.get(User, int(user_id))

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
@login_required
def hello():
     todos = Todo.query.all()
     completed = Completed.query.all()
     return render_template('home.html', todos=todos, completed=completed)

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']

          user = User.query.filter_by(username=username).first()
          if not user:
               flash('Invalid User.', 'error')
          else:
               password_correct = bcrypt.check_password_hash(user.password_hash, password)
               if not password_correct:
                    flash('Invalid Password.', 'error')
               else:
                    login_user(user)
                    flash('Login Successfull.', 'success')
                    return redirect('/')


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
@login_required
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
@login_required
def handle_complete(id):
     todo = Todo.query.get(id)
     completed = Completed(title=todo.title, description = todo.description)
     db.session.add(completed)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def handle_delete(id):
     todo = Todo.query.get(id)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/delete_comp/<int:id>')
@login_required
def handle_delete_comp(id):
     todo = Completed.query.get(id)
     db.session.delete(todo)
     db.session.commit()
     return redirect('/')

@app.route('/clear_completed')
@login_required
def handle_clear_completed():
     todos = Completed.query.delete()
     db.session.commit()
     return redirect('/')

@app.route('/logout')
@login_required
def handle_logout():
     logout_user()
     flash('Logout successfull.', 'success')
     return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)