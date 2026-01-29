# 📚 FoodApp Project - Complete File Structure & Explanation

## 🎯 Project Overview

**HomeFood Connect** is a Django-based web platform that connects home cooks with local buyers for authentic home-cooked meal delivery through a self-pickup model.

---

## 📁 Project Structure

```
FoodApp/
├── manage.py                          # Django command-line utility
├── requirements.txt                   # Python dependencies
├── db.sqlite3                         # SQLite database (development)
├── DbTable.txt                        # Database schema documentation
├── view_db.py                         # Script to view database content
├── .env                               # Environment variables (LOCAL)
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
│
├── homefood/                          # Main Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Django configuration
│   ├── urls.py                        # Main URL router
│   ├── wsgi.py                        # WSGI application
│   ├── asgi.py                        # ASGI application
│   └── context_processors.py          # Context processors for templates
│
├── apps/                              # Django applications
│   ├── accounts/                      # User authentication & profiles
│   ├── buyers/                        # Buyer functionality
│   ├── cooks/                         # Cook functionality
│   ├── admin_panel/                   # Admin dashboard
│   ├── payments/                      # Payment processing
│   ├── ml_engine/                     # Machine learning services
│   └── notifications/                 # Notification services
│
├── templates/                         # HTML templates
│   ├── base.html                      # Base template
│   ├── accounts/                      # Auth templates
│   ├── buyers/                        # Buyer templates
│   ├── cooks/                         # Cook templates
│   ├── admin_panel/                   # Admin templates
│   └── payments/                      # Payment templates
│
├── static/                            # Static files
│   ├── css/                           # Stylesheets
│   └── js/                            # JavaScript files
│
├── media/                             # User-uploaded files
│   ├── meal_images/                   # Meal photos
│   ├── fssai_certificates/            # FSSAI certificates
│   └── review_food_photos/            # Review photos
│
└── Documentation Files                # Guide documents
    ├── README.md
    ├── ABSTRACT.md
    ├── SETUP_GUIDE.md
    ├── QUICK_START.md
    └── REVIEW_SYSTEM_*.md
```

---

## 📄 Root Level Files

### 1. **[manage.py](manage.py)**
- **Purpose:** Django command-line utility for administrative tasks
- **Usage:** 
  ```bash
  python manage.py runserver      # Start development server
  python manage.py migrate        # Apply database migrations
  python manage.py createsuperuser # Create admin user
  ```

### 2. **[requirements.txt](requirements.txt)**
- **Purpose:** Lists all Python package dependencies
- **Contains:** Django, database drivers, ML libraries, payment APIs, etc.
- **Usage:** 
  ```bash
  pip install -r requirements.txt
  ```

### 3. **[db.sqlite3](db.sqlite3)**
- **Purpose:** SQLite database file (development only)
- **Contains:** All application data (users, orders, reviews, etc.)
- **Note:** For production, use MySQL instead

### 4. **[DbTable.txt](DbTable.txt)**
- **Purpose:** Documentation of database schema
- **Contains:** List of all tables and their structure

### 5. **[view_db.py](view_db.py)**
- **Purpose:** Utility script to view database content
- **Usage:** Run to inspect data in development

### 6. **[.env](/.env)**
- **Purpose:** Local environment variables (⚠️ Never commit to git)
- **Contains:** 
  - `SECRET_KEY` - Django secret key
  - `DEBUG` - Debug mode flag
  - `DATABASE_URL` - Database connection string
  - API keys (Razorpay, Google Maps, MSG91, etc.)

### 7. **[.env.example](.env.example)**
- **Purpose:** Template for environment variables
- **Usage:** Copy to `.env` and fill in actual values

### 8. **[.gitignore](.gitignore)**
- **Purpose:** Specifies files to ignore in git
- **Excludes:** `.env`, `*.pyc`, `db.sqlite3`, `media/`, `__pycache__/`

---

## 🏢 Core Configuration - [homefood/](homefood/)

### **[homefood/settings.py](homefood/settings.py)** - Main Configuration
**Purpose:** Central Django configuration file

**Key Settings:**
```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'homefood_db',
        'USER': 'root',
        'PASSWORD': '...',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Installed Apps (7 custom apps)
INSTALLED_APPS = [
    'apps.accounts',      # User management
    'apps.buyers',        # Buyer features
    'apps.cooks',         # Cook features
    'apps.admin_panel',   # Admin features
    'apps.payments',      # Payment processing
    'apps.ml_engine',     # ML/AI features
    'apps.notifications', # Alerts & notifications
]

# Static & Media Files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'

# FSSAI Verification Settings
FSSAI_OCR_CONFIDENCE_THRESHOLD = 0.6
FSSAI_NUMBER_LENGTH = 14
```

### **[homefood/urls.py](homefood/urls.py)** - Main URL Router
**Purpose:** Routes all URLs to appropriate app views

**Contains:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin
    path('accounts/', include('apps.accounts.urls')),     # Auth
    path('buyers/', include('apps.buyers.urls')),         # Buyer features
    path('cooks/', include('apps.cooks.urls')),           # Cook features
    path('payments/', include('apps.payments.urls')),     # Payments
]
```

### **[homefood/wsgi.py](homefood/wsgi.py)**
- **Purpose:** WSGI (Web Server Gateway Interface) configuration
- **Usage:** For production deployment with web servers like Gunicorn

### **[homefood/asgi.py](homefood/asgi.py)**
- **Purpose:** ASGI configuration (for async support)
- **Usage:** For real-time features like notifications

### **[homefood/context_processors.py](homefood/context_processors.py)**
- **Purpose:** Provides data to all templates
- **Contains:** Google Maps API key, global settings

---

## 📱 Applications - [apps/](apps/)

### **[apps/accounts/](apps/accounts/)** - User Authentication & Profiles

**Files:**
- **[models.py](apps/accounts/models.py)**
  - `User` - Custom user model with `user_type` (cook/buyer)
  - `CookProfile` - Extended profile for cooks
    - Fields: address, city, latitude, longitude, rating, FSSAI certificate
  - `BuyerProfile` - Profile for buyers
    - Fields: preferences, dietary restrictions

- **[views.py](apps/accounts/views.py)**
  - `register` - User registration
  - `login` - User login
  - `profile` - View/edit profile
  - `edit_profile` - Update personal info
  - `edit_fssai_certificate` - Upload FSSAI certificate

- **[forms.py](apps/accounts/forms.py)**
  - `UserRegistrationForm` - Registration form
  - `UserLoginForm` - Login form
  - `CookProfileForm` - Cook profile form
  - `BuyerProfileForm` - Buyer profile form

- **[urls.py](apps/accounts/urls.py)**
  - Routes for registration, login, logout, profile pages

- **[admin.py](apps/accounts/admin.py)**
  - Admin interface for managing users

- **Migrations/** - Database schema changes

---

### **[apps/buyers/](apps/buyers/)** - Buyer Features

**Files:**
- **[models.py](apps/buyers/models.py)**
  - `BuyerOrder` - Customer orders
    - Fields: buyer, meal, cook, quantity, status, total_amount, payment_method
    - Statuses: pending, accepted, preparing, ready, completed, cancelled
  - `BuyerReview` - Reviews & ratings
    - Overall rating (1-5), questionnaire ratings, comments, photos
    - Sentiment score (AI-generated)
  - `FavoriteCook` - Bookmarked cooks
  - `SearchHistory` - Track user searches

- **[views.py](apps/buyers/views.py)**
  - `home` - Homepage with featured meals
  - `search` - Search meals by location/name
  - `meal_detail` - View single meal details
  - `cook_profile` - View cook's profile & meals
  - `create_order` - Place order
  - `order_list` - View all orders
  - `order_detail` - View single order
  - `add_review` - Submit review for completed order ⭐ NEW
  - `recommendations` - ML-based meal suggestions
  - `api_nearby_meals` - API for location-based search

- **[forms.py](apps/buyers/forms.py)**
  - `SearchForm` - Meal search form
  - `BuyerReviewForm` - Review submission form ⭐ NEW (enhanced)

- **[urls.py](apps/buyers/urls.py)**
  - Routes for all buyer features

- **Templates/** - HTML for buyer features

---

### **[apps/cooks/](apps/cooks/)** - Cook Features

**Files:**
- **[models.py](apps/cooks/models.py)**
  - `Meal` - Cook's meal listings
    - Fields: name, description, price, ingredients, category, images
  - `MealImage` - Multiple images per meal
  - `PickupSlot` - Available pickup times & quantities
  - `CookOrder` - Orders received by cooks
  - `CookReview` - Reviews visible to cooks
  - `CookAnalytics` - Sales & performance data

- **[views.py](apps/cooks/views.py)**
  - `dashboard` - Cook's main dashboard
  - `meal_list` - View all their meals
  - `meal_create` - Add new meal
  - `meal_edit` - Edit existing meal
  - `meal_delete` - Delete meal
  - `order_list` - View orders received
  - `update_order_status` - Change order status
  - `pickup_slots` - Manage pickup times
  - `analytics` - View sales analytics
  - `reviews` - View customer reviews

- **[forms.py](apps/cooks/forms.py)**
  - `MealForm` - Add/edit meals
  - `PickupSlotForm` - Set pickup times

- **[signals.py](apps/cooks/signals.py)**
  - Auto-create CookProfile when user registers
  - Auto-update analytics when orders change

- **[urls.py](apps/cooks/urls.py)**
  - Routes for cook dashboard & features

- **Templates/** - HTML for cook features

---

### **[apps/payments/](apps/payments/)** - Payment Processing

**Files:**
- **[models.py](apps/payments/models.py)**
  - `Payment` - Payment records
    - Fields: order, amount, payment_method, status, transaction_id
    - Methods: online (Razorpay) or cash on pickup

- **[views.py](apps/payments/views.py)**
  - `process` - Initiate Razorpay payment
  - `success` - Handle successful payment
  - `failure` - Handle failed payment
  - `cash_payment` - Record cash payment

- **[forms.py](apps/payments/forms.py)**
  - `PaymentForm` - Payment details form

- **[urls.py](apps/payments/urls.py)**
  - Routes for payment processing

- **Templates/** - Payment success/failure pages

---

### **[apps/ml_engine/](apps/ml_engine/)** - Machine Learning Services

**Files:**
- **[models.py](apps/ml_engine/models.py)**
  - `MLModel` - Store trained ML models
  - `UserBehavior` - Track user interactions
  - `DemandForecast` - Predicted demand for meals

- **[ml_services.py](apps/ml_engine/ml_services.py)** - Core ML Logic
  - `RecommendationService` - Collaborative filtering recommendations
  - `DemandForecastService` - Prophet-based demand prediction
  - `SentimentAnalysisService` - TextBlob sentiment analysis
  - Methods for meal suggestions based on user history

- **[services/]()** - Additional ML utilities
  - Vectorization helpers
  - Feature extraction
  - Model training scripts

---

### **[apps/admin_panel/](apps/admin_panel/)** - Admin Dashboard

**Files:**
- **[models.py](apps/admin_panel/models.py)**
  - `AdminAction` - Log admin activities

- **[views.py](apps/admin_panel/views.py)**
  - `dashboard` - Admin overview
  - `user_list` - Manage users
  - `cook_verification_list` - Verify cooks
  - `order_list` - View all orders
  - `analytics` - Platform analytics
  - `dispute_list` - Handle disputes

- **[urls.py](apps/admin_panel/urls.py)**
  - Admin routes

- **Templates/** - Admin pages

---

### **[apps/notifications/](apps/notifications/)** - Notifications & Alerts

**Files:**
- **[services.py](apps/notifications/services.py)**
  - `send_order_notification` - Alert cook of new order
  - `send_payment_alert` - Payment confirmation
  - `send_sms` - MSG91 SMS integration
  - `send_whatsapp` - WhatsApp messages
  - Email notifications

---

## 🎨 Templates - [templates/](templates/)

### **[templates/base.html](templates/base.html)**
- **Purpose:** Master template for all pages
- **Contains:**
  - Navigation bar
  - Footer
  - CSS & JS includes
  - Flash message display
  - Block areas for child templates

### **[templates/accounts/](templates/accounts/)**
- `login.html` - Login page
- `register.html` - Registration page
- `profile.html` - View profile
- `edit_profile.html` - Edit profile
- `edit_fssai_certificate.html` - Upload FSSAI cert

### **[templates/buyers/](templates/buyers/)**
- `home.html` - Buyer homepage
- `search.html` - Search results
- `meal_detail.html` - Single meal view
- `cook_profile.html` - Cook profile & meals
- `order_list.html` - My orders
- `order_detail.html` - Order details ⭐ ENHANCED
- `add_review.html` - Submit review ⭐ ENHANCED
- `favorites.html` - Saved cooks
- `recommendations.html` - Suggested meals
- `nearby.html` - Map view of nearby cooks

### **[templates/cooks/](templates/cooks/)**
- `dashboard.html` - Cook homepage
- `meal_list.html` - My meals
- `meal_form.html` - Add/edit meal
- `meal_confirm_delete.html` - Delete confirmation
- `order_list.html` - Orders received
- `pickup_slots.html` - Manage time slots
- `analytics.html` - Sales dashboard
- `reviews.html` - Customer reviews

### **[templates/admin_panel/](templates/admin_panel/)**
- `dashboard.html` - Admin overview
- `user_list.html` - Manage users
- `cook_verification_list.html` - Verify cooks
- `order_list.html` - All orders
- `dispute_list.html` - Handle disputes
- `analytics.html` - Platform stats

### **[templates/payments/](templates/payments/)**
- `process.html` - Payment page (Razorpay integration)
- `success.html` - Payment successful
- `failure.html` - Payment failed

---

## 🎨 Static Files - [static/](static/)

### **[static/css/](static/css/)**
- **[custom.css](static/css/custom.css)** - Custom styles
- **[foodied.css](static/css/foodied.css)** - Additional styling

### **[static/js/](static/js/)**
- **[buyer_home.js](static/js/buyer_home.js)** - Homepage interactivity
- **[buyer_nearby.js](static/js/buyer_nearby.js)** - Map & location features

---

## 📂 Media Files - [media/](media/)

### **[media/meal_images/](media/meal_images/)**
- Uploaded photos of meals by cooks

### **[media/fssai_certificates/](media/fssai_certificates/)**
- FSSAI license documents of cooks

### **[media/review_food_photos/](media/review_food_photos/)**
- Photos uploaded with customer reviews

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview & setup instructions |
| [ABSTRACT.md](ABSTRACT.md) | Detailed system description |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Installation & configuration guide |
| [QUICK_START.md](QUICK_START.md) | Quick setup for new developers |
| [START_HERE.md](START_HERE.md) | Entry point documentation |
| [REVIEW_SYSTEM_GUIDE.md](REVIEW_SYSTEM_GUIDE.md) | Review feature guide |
| [CODE_CHANGES_SUMMARY.md](CODE_CHANGES_SUMMARY.md) | Recent code modifications |

---

## 🔄 Key Workflows

### **User Registration Flow**
```
Register (form) → accounts/views.py → User model → Database → Email verification
```

### **Order Placement Flow**
```
Browse Meals → Add to Cart → Checkout → Payment (Razorpay/Cash) → Order Created → Notification to Cook
```

### **Review Submission Flow**
```
Order Completed → Add Review Button → buyers/forms.py → Sentiment Analysis → Cook Rating Updated
```

### **Recommendation Flow**
```
User Behavior → ML Engine → Collaborative Filtering → Personalized Suggestions
```

---

## 🛠️ Tech Stack Summary

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.0 (Python) |
| **Database** | MySQL 8.0 (SQLite for dev) |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Payments** | Razorpay API |
| **Maps** | Google Maps JavaScript API |
| **Notifications** | MSG91 (SMS/WhatsApp) |
| **ML Libraries** | Scikit-learn, Prophet, TextBlob, Pandas |
| **Charts** | Chart.js |

---

## 🚀 How to Navigate the Project

### For New Developers:
1. Start with [README.md](README.md)
2. Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Review [homefood/settings.py](homefood/settings.py)
4. Explore [apps/accounts/](apps/accounts/) first
5. Then explore [apps/buyers/](apps/buyers/)

### For Feature Additions:
1. Identify which app is affected
2. Update models.py if schema changes
3. Update views.py for logic
4. Create templates as needed
5. Add URLs to urls.py
6. Test thoroughly

### For Bug Fixes:
1. Check which app is affected
2. Review views.py and models.py
3. Check templates for UI issues
4. Use Django shell for debugging

---

## 📊 Database Models Overview

```
User (accounts)
  ├── CookProfile (accounts)
  │   ├── Meal (cooks)
  │   │   ├── MealImage (cooks)
  │   │   ├── PickupSlot (cooks)
  │   │   ├── BuyerOrder (buyers)
  │   │   │   ├── BuyerReview (buyers) ⭐ NEW
  │   │   │   └── Payment (payments)
  │   │   └── CookOrder (cooks)
  │   │       └── CookReview (cooks)
  │   └── CookAnalytics (cooks)
  │
  └── BuyerProfile (buyers)
      ├── BuyerOrder (buyers)
      ├── FavoriteCook (buyers)
      ├── SearchHistory (buyers)
      └── UserBehavior (ml_engine)
```

---

**This comprehensive guide covers all files and their purposes in the FoodApp project!** 🎉

