from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_bcrypt import Bcrypt
from verification import verify_username, verify_password
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
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

# Flask app and extension setup
app = Flask(__name__)
app.secret_key = secrets.token_hex()  # Secure random secret key for session management

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# SQLAlchemy database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  # Default (todos) database
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users_db.db'   # Separate users database (not used for FK)
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.
    Loads a user by their user_id for session management.
    """
    return User.get(user_id)

class User(db.Model, UserMixin):
    """
    User model for authentication.
    Stores user credentials and relationship to todos.
    """
    __tablename__ = 'users_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(), nullable=False)

    # Relationship to Todo items (one-to-many)
    todos = relationship('Todo', back_populates='user', lazy='dynamic')

    @staticmethod
    def get(user_id):
        """
        Static method to get a user by ID.
        Used by Flask-Login's user_loader.
        """
        return db.session.get(User, int(user_id))

    def __repr__(self):
        return f"<ID {self.id} - username {self.username}>"

class Todo(db.Model):
    """
    Todo model for storing todo items.
    Each todo is linked to a user via a foreign key.
    """
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Date, default=datetime.utcnow().date)
    is_completed = db.Column(db.Boolean, default=False)

    # Foreign key to User table
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)

    # Relationship to User
    user = relationship('User', back_populates='todos')

    def __repr__(self):
        return f"<Todo {self.id} - {self.title}>"

@app.route('/')
@login_required
def hello():
    """
    Home route.
    Displays all active and completed todos for the logged-in user.
    """
    user = User.query.filter_by(username=current_user.username).first()
    todos = user.todos.filter_by(is_completed=False).all()
    completed = user.todos.filter_by(is_completed=True).all()
    return render_template('home.html', todos=todos, completed=completed)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route.
    Handles user login via POST and renders login form via GET.
    """
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
    """
    Signup route.
    Handles user registration via POST and renders signup form via GET.
    Validates username and password, checks for duplicates, and creates a new user.
    """
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
    """
    Handles submission of a new todo item.
    Requires user to be logged in.
    """
    try:
        title = request.form['title']
        desc = request.form['description']
        if not title or not desc:
            return "Title and description are required.", 400
        
        user = User.query.filter_by(username=current_user.username).first()
        todo = Todo(title=title, description=desc, user=user)
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
    """
    Marks a todo item as completed.
    """
    todo = db.get_or_404(Todo, id)
    todo.is_completed = True
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def handle_delete(id):
    """
    Deletes an active todo item.
    """
    todo = db.get_or_404(Todo, id)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/delete_comp/<int:id>')
@login_required
def handle_delete_comp(id):
    """
    Deletes a completed todo item.
    """
    todo = db.get_or_404(Todo, id)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/clear_completed')
@login_required
def handle_clear_completed():
    """
    Deletes all completed todo items for the current user.
    """
    delete_stmt = db.delete(Todo).filter_by(is_completed=True)
    db.session.execute(delete_stmt)
    db.session.commit()
    return redirect('/')

@app.route('/logout')
@login_required
def handle_logout():
    """
    Logs out the current user and redirects to the login page.
    """
    logout_user()
    flash('Logout successfull.', 'success')
    return redirect('/login')

if __name__ == '__main__':
    # Create all tables for the app (users and todos)
    with app.app_context():
        db.create_all(bind_key='users')  # Create users table if using bind
        db.create_all()                  # Create all other tables
    app.run(debug=True)