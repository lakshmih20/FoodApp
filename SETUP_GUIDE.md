# HomeFood Connect - Setup & Run Guide

## Prerequisites

Before running this project, ensure you have the following installed:

1. **Python 3.8+** (Python 3.13.7 is recommended)
2. **MySQL 8.0** server installed and running
3. **pip** (Python package manager)
4. **Git** (optional, for version control)

## Step-by-Step Setup Instructions

### Step 1: Verify Python Installation

Open your terminal/command prompt and check Python version:

```bash
python --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Install MySQL Database

1. Download and install MySQL 8.0 from [mysql.com](https://dev.mysql.com/downloads/mysql/)
2. Start MySQL service
3. Create a database for the project:

```sql
CREATE DATABASE homefood_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or using MySQL command line:
```bash
mysql -u root -p
CREATE DATABASE homefood_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Step 3: Install Python Dependencies

Navigate to the project directory and install all required packages:

```bash
cd C:\Users\laksh\Downloads\FoodApp
pip install -r requirements.txt
```

**Note:** If you encounter issues with `mysqlclient`, you may need to install it separately:

**For Windows:**
- Download the appropriate wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient)
- Install it: `pip install mysqlclient‑2.2.0‑cp313‑cp313‑win_amd64.whl` (adjust version for your Python)

**Alternative:** Use `pymysql` instead:
```bash
pip install pymysql
```
Then add this to `homefood/settings.py` at the top:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Step 4: Configure Environment Variables

1. Create a `.env` file in the project root directory (same level as `manage.py`)
2. Copy the following template and fill in your values:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=homefood_db
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

# Razorpay Configuration (Optional - for payment features)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Google Maps API (Optional - for location features)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# MSG91 Configuration (Optional - for notifications)
MSG91_AUTH_KEY=your-msg91-auth-key
MSG91_SENDER_ID=your-sender-id
```

**Important:** 
- Replace `your-mysql-password` with your actual MySQL root password
- Generate a secure SECRET_KEY (you can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- API keys are optional but required for full functionality

### Step 5: Create Database Migrations

Run the following commands to create and apply database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create all necessary database tables.

### Step 6: Create Media Directories

Create the media directories for file uploads:

```bash
mkdir media
mkdir media\meal_images
mkdir media\profile_images
```

Or manually create these folders in the project root.

### Step 7: Create Superuser (Admin Account)

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email (optional)
- Password (will be hidden)

### Step 8: Collect Static Files (Optional)

Collect static files for production (optional for development):

```bash
python manage.py collectstatic
```

### Step 9: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 10: Access the Application

Open your web browser and navigate to:

- **Home Page:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Buyer Home:** http://127.0.0.1:8000/buyers/
- **Cook Dashboard:** http://127.0.0.1:8000/cooks/dashboard/ (requires login as cook)

## Quick Start Commands Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your database credentials

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create media directories
mkdir media\meal_images
mkdir media\profile_images

# 5. Create superuser
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

## Testing the Application

### 1. Create Test Users

1. Go to http://127.0.0.1:8000/accounts/register/
2. Register as a **Buyer** user
3. Register as a **Cook** user (different account)
4. Login as the cook and complete the cook profile

### 2. Test Cook Features

1. Login as a cook
2. Go to Dashboard
3. Add a meal
4. Create pickup slots
5. View orders

### 3. Test Buyer Features

1. Login as a buyer
2. Browse meals
3. Place an order
4. View order status

### 4. Test Admin Features

1. Login as superuser
2. Go to http://127.0.0.1:8000/admin/
3. Verify cook profiles
4. Approve cook verifications

## Troubleshooting

### Issue: `mysqlclient` installation fails

**Solution:** Use `pymysql` instead:
```bash
pip install pymysql
```
Add to `homefood/settings.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Issue: Database connection error

**Solution:** 
- Check MySQL is running
- Verify database credentials in `.env`
- Ensure database `homefood_db` exists

### Issue: Module not found errors

**Solution:** 
- Ensure you're in the project directory
- Activate virtual environment if using one
- Reinstall requirements: `pip install -r requirements.txt`

### Issue: Migration errors

**Solution:**
```bash
python manage.py makemigrations --name initial
python manage.py migrate
```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --noinput
```

## Development Tips

1. **Use Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Enable Debug Mode:** Already set to `True` in `.env` for development

3. **View Logs:** Check terminal output for errors and debug information

4. **Database Admin:** Use Django admin at `/admin/` or MySQL Workbench

## Production Deployment Notes

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Configure proper static file serving
5. Use environment variables for all secrets
6. Set up SSL/HTTPS
7. Configure proper database backups

## Support

If you encounter any issues, check:
- Django documentation: https://docs.djangoproject.com/
- MySQL documentation: https://dev.mysql.com/doc/
- Project README.md for additional information

