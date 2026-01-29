# 🎯 FoodApp - Quick File Reference Guide

## 📋 One-Page Overview

### **7 Django Apps + Configuration**

| App | Purpose | Key Files |
|-----|---------|-----------|
| **accounts** | User registration, login, profiles | models, views, forms, urls |
| **buyers** | Search meals, order, review | models, views, forms, urls |
| **cooks** | List meals, manage orders, analytics | models, views, forms, urls |
| **payments** | Process payments (Razorpay, Cash) | models, views, forms, urls |
| **ml_engine** | Recommendations, forecasting, sentiment | ml_services.py, models |
| **admin_panel** | Admin dashboard, moderation | views, templates |
| **notifications** | SMS, Email, alerts | services.py |

---

## 🗂️ Essential Files by Task

### **I need to...**

**...add a new field to User**
→ Edit [apps/accounts/models.py](apps/accounts/models.py)
→ Create migration: `python manage.py makemigrations`
→ Apply: `python manage.py migrate`

**...change the login page**
→ Edit [templates/accounts/login.html](templates/accounts/login.html)
→ Update styling in [static/css/custom.css](static/css/custom.css)

**...add new buyer feature**
→ Add model to [apps/buyers/models.py](apps/buyers/models.py)
→ Add view to [apps/buyers/views.py](apps/buyers/views.py)
→ Add form to [apps/buyers/forms.py](apps/buyers/forms.py)
→ Add template to [templates/buyers/](templates/buyers/)
→ Add URL to [apps/buyers/urls.py](apps/buyers/urls.py)

**...create admin dashboard**
→ Add view to [apps/admin_panel/views.py](apps/admin_panel/views.py)
→ Add template to [templates/admin_panel/](templates/admin_panel/)

**...improve recommendation algorithm**
→ Edit [apps/ml_engine/ml_services.py](apps/ml_engine/ml_services.py)

**...add email notifications**
→ Edit [apps/notifications/services.py](apps/notifications/services.py)

**...integrate payment gateway**
→ Edit [apps/payments/views.py](apps/payments/views.py)

---

## 🔍 File Quick Lookup

### **Configuration Files**
```
homefood/settings.py        ← Database, installed apps, API keys
homefood/urls.py            ← Main URL routing
.env                        ← Local secrets (never commit!)
requirements.txt            ← Python packages
```

### **Django Apps Structure** (Repeat for each app)
```
apps/<app_name>/
├── models.py              ← Database tables
├── views.py               ← Business logic
├── forms.py               ← HTML forms
├── urls.py                ← URL routing
├── admin.py               ← Admin interface
├── apps.py                ← App config
├── signals.py             ← Event handlers
└── migrations/            ← Database versions
```

### **Frontend Files**
```
templates/base.html         ← Master template
templates/<app>/            ← App templates
static/css/                 ← Stylesheets
static/js/                  ← JavaScript
media/                      ← User uploads
```

---

## 📊 Models Quick Reference

### **User & Profile Models**
```python
User (accounts/models.py)
  ├─ username, email, password
  ├─ user_type: 'cook' or 'buyer'
  └─ is_verified, is_active

CookProfile (accounts/models.py)
  ├─ user (FK)
  ├─ address, city, latitude, longitude
  ├─ rating, total_reviews
  ├─ fssai_certificate
  └─ is_verified

BuyerProfile (accounts/models.py)
  ├─ user (FK)
  ├─ preferences
  └─ dietary_restrictions
```

### **Meal & Order Models**
```python
Meal (cooks/models.py)
  ├─ cook (FK)
  ├─ name, description, price
  ├─ ingredients, category
  └─ is_available

PickupSlot (cooks/models.py)
  ├─ meal (FK)
  ├─ date, start_time, end_time
  └─ available_quantity

BuyerOrder (buyers/models.py)
  ├─ buyer, cook, meal
  ├─ quantity, total_amount
  ├─ status (pending/accepted/completed/etc)
  ├─ payment_method (online/cash)
  └─ created_at

BuyerReview (buyers/models.py) ⭐ NEW
  ├─ order (FK, OneToOne)
  ├─ overall_rating (1-5) - Required
  ├─ freshness_rating (1-5) - Optional
  ├─ hygiene_rating (1-5) - Optional
  ├─ taste_rating (1-5) - Optional
  ├─ packaging_rating (1-5) - Optional
  ├─ comment (text) - Optional
  ├─ food_photo (image) - Optional
  ├─ sentiment_score (0-1) - Auto-generated
  └─ created_at
```

### **Payment & Analytics Models**
```python
Payment (payments/models.py)
  ├─ order (FK)
  ├─ amount, status
  ├─ payment_method (online/cash)
  ├─ transaction_id
  └─ created_at

CookAnalytics (cooks/models.py)
  ├─ cook (FK)
  ├─ total_orders, total_revenue
  ├─ avg_rating
  └─ last_updated
```

---

## 🔄 Common Operations

### **Create a New Order (in views)**
```python
# In apps/buyers/views.py
from apps.buyers.models import BuyerOrder
from apps.cooks.models import Meal, PickupSlot

order = BuyerOrder.objects.create(
    buyer=request.user,
    meal=Meal.objects.get(id=meal_id),
    cook=meal.cook,
    pickup_slot=PickupSlot.objects.get(id=slot_id),
    quantity=int(request.POST.get('quantity')),
    total_amount=meal.price * quantity,
    status='pending',
    payment_method=request.POST.get('payment_method')
)
```

### **Get User's Orders (in views)**
```python
orders = BuyerOrder.objects.filter(
    buyer=request.user
).order_by('-created_at')
```

### **Add a Review (in views)**
```python
# Already implemented in apps/buyers/views.py
review = BuyerReview.objects.create(
    order=order,
    overall_rating=form.cleaned_data['overall_rating'],
    comment=form.cleaned_data['comment'],
    food_photo=form.cleaned_data['food_photo'],
    # ...other fields
)
```

### **Query ML Recommendations**
```python
from apps.ml_engine.ml_services import RecommendationService

service = RecommendationService()
recommendations = service.get_recommendations(user=request.user)
```

### **Send Notification**
```python
from apps.notifications.services import send_order_notification

send_order_notification(
    order=order,
    notification_type='new_order'
)
```

---

## 🗺️ URL Patterns

### **Buyer URLs** (apps/buyers/urls.py)
```
/buyers/                        → Home page
/buyers/search/                 → Search results
/buyers/meals/<id>/             → Meal details
/buyers/cook/<id>/              → Cook profile
/buyers/orders/                 → My orders list
/buyers/orders/<id>/            → Order details
/buyers/orders/<id>/review/     → Add review ⭐ NEW
/buyers/favorites/              → Saved cooks
/buyers/recommendations/        → Suggested meals
```

### **Cook URLs** (apps/cooks/urls.py)
```
/cooks/dashboard/               → Cook homepage
/cooks/meals/                   → My meals
/cooks/meals/create/            → Add meal
/cooks/meals/<id>/edit/         → Edit meal
/cooks/orders/                  → Orders received
/cooks/analytics/               → Sales dashboard
/cooks/reviews/                 → Customer reviews
```

### **Auth URLs** (apps/accounts/urls.py)
```
/accounts/register/             → Sign up
/accounts/login/                → Sign in
/accounts/logout/               → Sign out
/accounts/profile/              → View profile
/accounts/profile/edit/         → Edit profile
```

### **Payment URLs** (apps/payments/urls.py)
```
/payments/process/<order_id>/   → Process payment
/payments/success/              → Success page
/payments/failure/              → Failure page
```

### **Admin URLs** (apps/admin_panel/urls.py)
```
/admin/dashboard/               → Admin home
/admin/users/                   → Manage users
/admin/verify-cooks/            → Verify cooks
/admin/orders/                  → View all orders
```

---

## 📝 Template Hierarchy

```
base.html (Master)
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── edit_profile.html
├── buyers/
│   ├── home.html
│   ├── search.html
│   ├── meal_detail.html
│   ├── cook_profile.html
│   ├── order_list.html
│   ├── order_detail.html
│   ├── add_review.html ⭐ NEW (Enhanced)
│   ├── favorites.html
│   ├── recommendations.html
│   └── nearby.html
├── cooks/
│   ├── dashboard.html
│   ├── meal_list.html
│   ├── meal_form.html
│   ├── order_list.html
│   ├── pickup_slots.html
│   ├── analytics.html
│   └── reviews.html
├── admin_panel/
│   ├── dashboard.html
│   ├── user_list.html
│   ├── cook_verification_list.html
│   ├── order_list.html
│   └── dispute_list.html
└── payments/
    ├── process.html
    ├── success.html
    └── failure.html
```

---

## 🛠️ Development Commands

```bash
# Start development server
python manage.py runserver

# Create database migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Access Python shell
python manage.py shell

# Django admin
http://localhost:8000/admin/

# View logs/errors
# Check terminal output

# Clear database (DANGER!)
python manage.py migrate --fake-initial 0001
python manage.py migrate zero <app_name>
```

---

## 🔧 Configuration Files

### **Environment Variables** (.env)
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=mysql://user:pass@localhost/foodapp
RAZORPAY_KEY_ID=your-key
RAZORPAY_SECRET_KEY=your-secret
GOOGLE_MAPS_API_KEY=your-key
MSG91_AUTHKEY=your-key
EMAIL_HOST_PASSWORD=your-password
```

### **Dependencies** (requirements.txt)
```
Django==5.0
mysqlclient==2.2.0
razorpay==1.3.0
python-dotenv==1.0.0
scikit-learn==1.3.0
fbprophet==0.7.10
textblob==0.17.1
pandas==2.0.0
pillow==10.0.0
requests==2.31.0
```

---

## 📊 Database Schema

**7 Main Tables:**

1. **auth_user** - User accounts
2. **accounts_cookprofile** - Cook profiles
3. **accounts_buyerprofile** - Buyer profiles
4. **cooks_meal** - Meal listings
5. **cooks_pickupslot** - Available time slots
6. **buyers_buyerorder** - Customer orders
7. **buyers_buyerreview** - Reviews ⭐ NEW

**Additional Tables:**
- cooks_mealimage - Meal photos
- cooks_cookorder - Cook's view of orders
- cooks_cookreview - Reviews for cooks
- payments_payment - Payment records
- buyers_favoritetecook - Saved cooks
- buyers_searchhistory - Search logs
- ml_engine_userbehavior - User interactions
- notifications_* - Notification logs

---

## 🎯 Key Classes & Functions

### **Important View Functions**
```python
# accounts/views.py
- register(request)
- login(request)
- profile(request)
- edit_profile(request)

# buyers/views.py
- home(request)
- search(request)
- meal_detail(request, pk)
- cook_profile(request, cook_id)
- create_order(request, meal_id)
- order_list(request)
- order_detail(request, pk)
- add_review(request, pk) ⭐ NEW
- recommendations(request)

# cooks/views.py
- dashboard(request)
- meal_list(request)
- create_meal(request)
- edit_meal(request, pk)
- order_list(request)
- analytics(request)

# payments/views.py
- process(request, order_id)
- success(request)
- failure(request)

# admin_panel/views.py
- dashboard(request)
- user_list(request)
- cook_verification_list(request)
```

### **Important Model Methods**
```python
# BuyerOrder model
- __str__() - String representation
- get_status_display() - Readable status

# BuyerReview model (⭐ NEW)
- __str__() - String representation
- save() - Auto-calculations

# CookProfile model
- get_average_rating() - Calculate rating
- is_verified() - Check verification status
```

---

## 🎨 Static & Media Files

### **CSS Files** (static/css/)
- `custom.css` - Custom styling
- `foodied.css` - Additional styles (Bootstrap-based)

### **JavaScript** (static/js/)
- `buyer_home.js` - Homepage interactions
- `buyer_nearby.js` - Map functionality

### **Media Directories** (media/)
- `meal_images/` - Meal photos (uploaded by cooks)
- `fssai_certificates/` - License documents
- `review_food_photos/` - Review photos ⭐ NEW

---

## 📚 Documentation Files

| File | Contains |
|------|----------|
| README.md | Project overview |
| ABSTRACT.md | Detailed description |
| SETUP_GUIDE.md | Installation steps |
| QUICK_START.md | Quick setup |
| **PROJECT_FILES_EXPLAINED.md** | ← THIS FILE |
| PROJECT_ARCHITECTURE.md | Architecture diagrams |
| REVIEW_SYSTEM_GUIDE.md | Review feature |
| CODE_CHANGES_SUMMARY.md | Recent changes |

---

## ✨ New Features (Review System)

**Files Enhanced:**
- ✅ [apps/buyers/forms.py](apps/buyers/forms.py) - Form validation
- ✅ [templates/buyers/order_detail.html](templates/buyers/order_detail.html) - Review button
- ✅ [templates/buyers/add_review.html](templates/buyers/add_review.html) - Review form

**Models (Already existed):**
- ✅ BuyerReview (apps/buyers/models.py) - Review storage

**Views (Already existed):**
- ✅ add_review() (apps/buyers/views.py) - Review submission

---

**Everything you need to navigate the FoodApp project!** 🚀

Start with [PROJECT_FILES_EXPLAINED.md](PROJECT_FILES_EXPLAINED.md) for detailed information.

