from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

"""
A simple Flask-based Todo application with SQLite database integration.
Modules:
     - flask: Web framework for Python.
     - flask_sqlalchemy: SQLAlchemy integration for Flask.
     - datetime: For handling date and time.
Classes:
     Todo(db.Model):
          Represents a Todo item in the database.
          Attributes:
               id (int): Primary key.
               title (str): Title of the todo item (required).
               description (str): Description of the todo item (required).
               date_created (date): Date when the todo was created (defaults to current date).
          Methods:
               __repr__: Returns a string representation of the Todo instance.
Routes:
     '/' [GET]:
          Renders the home page displaying all todo items.
     '/' [POST]:
          Handles submission of new todo items via form.
          Validates input and adds new item to the database.
     '/delete/<int:id>' [GET]:
          Deletes the todo item with the specified ID.
Application Entry Point:
     - Creates database tables if they do not exist.
     - Runs the Flask development server in debug mode.
"""

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_BINDS'] = {
    'completed':        'sqlite:///completed_db.sqlite3',     # Second DB
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
     return render_template('home.html', todos=todos, completed = completed)

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