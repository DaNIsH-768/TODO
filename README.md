# TODO Application

A Flask-based Todo application with user authentication and task management features.

## Features

- 🔐 User registration and login with secure password hashing (bcrypt)
- ✅ Add, complete, and delete todo items
- 📊 Separate views for active and completed todos
- 🎨 Responsive Bootstrap UI with dark theme
- 💾 SQLite database with SQLAlchemy ORM

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DaNIsH-768/TODO.git
cd TODO
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

5. Run the application:
```bash
python main.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Deployment

This application is configured for easy deployment to various platforms.

### Deploy to Render

1. Fork this repository to your GitHub account

2. Sign up for a free account at [Render.com](https://render.com)

3. Create a new Web Service:
   - Connect your GitHub repository
   - Name: `todo-app` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`

4. Add environment variables (optional but recommended):
   - `SECRET_KEY`: A secure random string for session management
   - `FLASK_ENV`: Set to `production`

5. Deploy! Your app will be live at `https://your-app-name.onrender.com`

### Deploy to Railway

1. Sign up at [Railway.app](https://railway.app)

2. Click "New Project" → "Deploy from GitHub repo"

3. Select your forked repository

4. Railway will automatically detect the Python app and deploy it

5. Add environment variables in the Railway dashboard:
   - `SECRET_KEY`: A secure random string

### Deploy to Heroku

1. Install the Heroku CLI

2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-todo-app-name
```

4. Set environment variables:
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
```

5. Deploy:
```bash
git push heroku main
```

### Deploy to PythonAnywhere

1. Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)

2. Upload your code or clone from GitHub

3. Create a new web app with Manual Configuration (Python 3.11)

4. Configure the WSGI file to point to `main.py:app`

5. Install requirements in a virtual environment

6. Reload the web app

## Environment Variables

- `SECRET_KEY` (recommended): Secret key for Flask sessions
- `FLASK_ENV` (optional): Set to `production` or `development`
- `DATABASE_PATH` (optional): Path to store SQLite database files (default: `instance`)
- `PORT` (optional): Port to run the application on (default: 5000)

## Password Requirements

For security, passwords must:
- Be at least 8 characters long
- Contain at least one uppercase letter
- Contain at least one lowercase letter
- Contain at least one digit
- Contain at least one special character (!@#$%^&*(),.?":{}|<>)

## Username Requirements

Usernames must:
- Be between 3 and 20 characters
- Contain only letters, numbers, underscores, or dots
- Start with a letter

## API Endpoints

The application includes a health check endpoint for monitoring:

- `GET /health` - Returns application status (useful for deployment platforms)

## Project Structure

```
TODO/
├── main.py              # Main Flask application
├── verification.py      # Username and password validation
├── requirements.txt     # Python dependencies
├── Procfile            # Process file for deployment
├── runtime.txt         # Python version specification
├── render.yaml         # Render deployment configuration
├── .env.example        # Example environment variables
├── templates/          # HTML templates
│   ├── home.html       # Main todo interface
│   ├── login.html      # Login page
│   └── signup.html     # Registration page
├── instance/           # Database files (not in git)
└── README.md           # This file
```

## Technologies Used

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-Bcrypt**: Password hashing
- **Bootstrap 5**: Frontend UI framework
- **SQLite**: Database

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
