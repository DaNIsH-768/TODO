# Deployment Guide

This guide provides step-by-step instructions for deploying the TODO application to various platforms.

## Quick Start - Deploy to Render (Recommended)

Render offers a free tier with automatic deployments from GitHub.

### Option 1: One-Click Deploy

1. Click the Deploy to Render button (add this to your README):
   - Fork this repository to your GitHub account
   - Sign up for [Render](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Create Web Service"

### Option 2: Manual Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/TODO.git
   cd TODO
   ```

2. **Sign up for Render**
   - Go to [render.com](https://render.com) and create an account

3. **Create a New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `todo-app` (or your choice)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn main:app`
     - **Plan**: Free

4. **Add Environment Variables** (recommended)
   - Click "Environment" in the service settings
   - Add the following:
     - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
     - `FLASK_ENV`: `production`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for the build and deployment to complete
   - Your app will be available at `https://your-app-name.onrender.com`

## Deploy to Railway

Railway provides automatic deployments with a generous free tier.

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app) and sign up

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked TODO repository
   - Railway automatically detects the Python app

3. **Configure Environment Variables**
   - Go to your project settings
   - Add variables:
     - `SECRET_KEY`: Generate a secure random string
     - `FLASK_ENV`: `production`

4. **Access Your App**
   - Railway provides a public URL automatically
   - Find it in "Settings" → "Networking"

## Deploy to Heroku

Heroku is a popular platform with extensive documentation.

### Prerequisites
- Heroku CLI installed
- Heroku account

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create a Heroku App**
   ```bash
   cd TODO
   heroku create your-todo-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-secure-secret-key"
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Open Your App**
   ```bash
   heroku open
   ```

### Note on Database Persistence
Heroku's free tier has ephemeral filesystem, meaning the SQLite database will be reset on each deployment or dyno restart. For production use, consider:
- Using Heroku Postgres (free tier available)
- Modifying the app to use PostgreSQL instead of SQLite

## Deploy to PythonAnywhere

PythonAnywhere is a Python-specific hosting platform with a free tier.

1. **Sign up**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Create a free account

2. **Upload Your Code**
   - Open a Bash console
   - Clone your repository:
     ```bash
     git clone https://github.com/YOUR-USERNAME/TODO.git
     cd TODO
     ```

3. **Create a Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 todo-env
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select "Python 3.11"

5. **Configure WSGI File**
   - Click on the WSGI configuration file link
   - Replace the contents with:
     ```python
     import sys
     import os
     
     # Add your project directory to the path
     project_home = '/home/YOUR-USERNAME/TODO'
     if project_home not in sys.path:
         sys.path.insert(0, project_home)
     
     # Set environment variables
     os.environ['SECRET_KEY'] = 'your-secret-key-here'
     os.environ['FLASK_ENV'] = 'production'
     
     # Import the Flask app
     from main import app as application
     ```

6. **Set Virtual Environment**
   - In the "Web" tab, set the virtualenv path:
     ```
     /home/YOUR-USERNAME/.virtualenvs/todo-env
     ```

7. **Reload**
   - Click the "Reload" button
   - Your app will be available at `https://YOUR-USERNAME.pythonanywhere.com`

## Deploy to Vercel (Serverless)

Vercel supports Python applications but requires some additional configuration.

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

3. **Deploy**
   ```bash
   vercel
   ```

**Note**: SQLite doesn't work well with serverless platforms. Consider using a managed database service.

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Recommended | Random | Secret key for Flask sessions |
| `FLASK_ENV` | Optional | development | Environment mode (development/production) |
| `DATABASE_PATH` | Optional | instance | Directory for SQLite database files |
| `PORT` | Optional | 5000 | Port for the application |

## Database Considerations

The application uses SQLite by default, which is:
- ✅ Great for development and small deployments
- ✅ No configuration required
- ⚠️ Not suitable for high-traffic applications
- ⚠️ May not persist on some platforms (Heroku, serverless)

### For Production Use

Consider migrating to PostgreSQL or MySQL:

1. Update `requirements.txt`:
   ```
   psycopg2-binary==2.9.9  # For PostgreSQL
   ```

2. Update database URL in `main.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
       'DATABASE_URL',
       'sqlite:///todos.db'
   )
   ```

3. Set the `DATABASE_URL` environment variable on your platform

## Health Check

The application includes a health check endpoint at `/health` that returns:

```json
{
  "status": "ok",
  "message": "Application is running"
}
```

Use this for:
- Uptime monitoring
- Load balancer health checks
- Deployment verification

## Troubleshooting

### Database Errors
- Ensure the `instance` directory exists and is writable
- Check that `DATABASE_PATH` is set correctly
- Verify SQLite is available on the platform

### Port Binding Issues
- Most platforms set the `PORT` environment variable automatically
- The app will use `PORT` if set, otherwise defaults to 5000

### Secret Key Warnings
- Always set `SECRET_KEY` in production
- Generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"`

### Build Failures
- Check that `requirements.txt` is valid
- Ensure Python 3.11+ is available (check `runtime.txt`)
- Verify Procfile syntax

## Support

For issues or questions:
1. Check the [README.md](README.md) for general information
2. Review deployment platform documentation
3. Open an issue on GitHub

## Security Notes

- ✅ All dependencies are up-to-date with security patches
- ✅ CodeQL security scanning passed
- ✅ Password hashing with bcrypt
- ✅ CSRF protection via Flask
- ⚠️ Always use HTTPS in production
- ⚠️ Set a strong SECRET_KEY
- ⚠️ Don't commit .env files to git
