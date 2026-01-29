# Quick Start Guide - HomeFood Connect

## Fast Setup (5 Minutes)

### Option 1: Using SQLite (Easier - No MySQL Required)

1. **Install Python packages:**
   ```bash
   pip install Django==5.0 python-dotenv==1.0.0 Pillow==10.2.0
   ```

2. **Create .env file:**
   Create a file named `.env` in the project root with:
   ```env
   SECRET_KEY=django-insecure-change-this-in-production-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   USE_SQLITE=True
   ```

3. **Update settings for SQLite:**
   Edit `homefood/settings.py` and replace the DATABASES section with:
   ```python
   if os.getenv('USE_SQLITE', 'False') == 'True':
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }
   else:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.mysql',
               'NAME': os.getenv('DB_NAME', 'homefood_db'),
               'USER': os.getenv('DB_USER', 'root'),
               'PASSWORD': os.getenv('DB_PASSWORD', ''),
               'HOST': os.getenv('DB_HOST', 'localhost'),
               'PORT': os.getenv('DB_PORT', '3306'),
               'OPTIONS': {
                   'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
               },
           }
       }
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create media folders:**
   ```bash
   mkdir media
   mkdir media\meal_images
   mkdir media\profile_images
   ```

7. **Run server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the app:**
   - Open browser: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

---

### Option 2: Using MySQL (Full Setup)

1. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   If `mysqlclient` fails, use `pymysql`:
   ```bash
   pip install pymysql
   ```
   Then add to top of `homefood/settings.py`:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

2. **Create MySQL database:**
   ```sql
   CREATE DATABASE homefood_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Create .env file:**
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=homefood_db
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create media folders:**
   ```bash
   mkdir media\meal_images
   mkdir media\profile_images
   ```

7. **Run server:**
   ```bash
   python manage.py runserver
   ```

---

## Testing the Application

1. **Register as Buyer:**
   - Go to http://127.0.0.1:8000/accounts/register/
   - Select "Buyer" and register

2. **Register as Cook:**
   - Register another account as "Cook"
   - Login and complete cook profile

3. **Add Meals (as Cook):**
   - Login as cook
   - Go to Dashboard → Add New Meal
   - Upload images, set price, add pickup slots

4. **Place Order (as Buyer):**
   - Login as buyer
   - Browse meals
   - Place an order
   - Choose payment method

5. **Admin Panel:**
   - Login as superuser
   - Go to http://127.0.0.1:8000/admin/
   - Verify cook profiles

---

## Common Commands

```bash
# Start development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell
```

---

## Troubleshooting

**Error: No module named 'django'**
```bash
pip install Django==5.0
```

**Error: mysqlclient not found**
```bash
pip install pymysql
# Then add to settings.py: import pymysql; pymysql.install_as_MySQLdb()
```

**Error: Database connection failed**
- Check MySQL is running
- Verify .env file credentials
- For SQLite: Set `USE_SQLITE=True` in .env

**Error: Media files not found**
- Create `media/meal_images/` and `media/profile_images/` folders

---

## Next Steps

1. Configure API keys in `.env` for:
   - Razorpay (payments)
   - Google Maps (location search)
   - MSG91 (notifications)

### Google Maps setup (Nearby cooks)

1. In the Google Cloud Console, create or select a project.
2. Enable billing for the project — the Maps JavaScript API requires billing to be enabled.
3. Enable the following API: **Maps JavaScript API**.
4. Create an API key (Credentials → Create credentials → API key).
5. (Recommended for local testing) Under Key restrictions, add an HTTP referrer restriction such as:
   - `http://127.0.0.1:8000/*`
   - `http://localhost:8000/*`
6. Copy the key and add it to your `.env` (or `.env` from `.env.example`):

```env
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE
```

7. Restart the Django server:

```bash
python manage.py runserver
```

8. Verify in the browser:
   - Open the nearby page: `http://127.0.0.1:8000/buyers/nearby/`
   - Open the JavaScript console (F12 → Console). If Maps fails to load you'll see a clear error such as `MissingKeyMapError`, `ApiKeyNotActivatedMapError`, or a restriction-related error. Use that message to adjust the key or its restrictions.

9. If you see the map error "Sorry! Something went wrong." but no console error, make sure the `GOOGLE_MAPS_API_KEY` value is present in your `.env` and that `homefood/settings.py` loads environment variables (this project uses `python-dotenv`).

### Post-migration verification

After running `python manage.py migrate`:

```bash
python manage.py migrate
python manage.py showmigrations
```

- Confirm the migrations for `apps.accounts` (and others) are marked with an `X`.
- If a migration fails, run `python manage.py makemigrations` (if you changed models) then retry `migrate`.

If you'd like, copy `.env.example` to `.env` now and I can help you fill in the Google Maps key and restart the server.

2. Customize the application as needed

3. For production, see SETUP_GUIDE.md for deployment instructions

