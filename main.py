from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
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

@app.route('/')
def hello():
     todos = Todo.query.all()
     return render_template('home.html', todos=todos)

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
          return redirect('/')
     except Exception as e:
          db.session.rollback()
          return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)