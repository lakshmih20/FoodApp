# HomeFood Connect - Local Home-Cooked Meal Platform

HomeFood Connect is a web-based platform connecting home cooks with local buyers through a self-pickup model. The platform enables cooks to list daily meals while buyers discover authentic home-cooked food within their neighborhood.

## Features

- **For Cooks**: Menu management, pickup scheduling, demand forecasting, review analytics
- **For Buyers**: Location-based search, personalized recommendations, secure payments, real-time notifications
- **Platform Intelligence**: ML-based recommendation engine, festival-aware demand prediction, multilingual sentiment analysis
- **Admin Panel**: Cook verification, platform monitoring, dispute resolution

## Technology Stack

- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js
- Backend: Python Django 5.0 (MVC Architecture)
- Database: MySQL 8.0
- Payments: Razorpay with Cash-on-Pickup option
- Maps: Google Maps JavaScript API
- ML Libraries: Scikit-learn, Prophet, TextBlob, Pandas
- Notifications: MSG91 SMS/WhatsApp API

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example` and configure your settings
4. Set up MySQL database
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
FoodApp/
├── manage.py
├── requirements.txt
├── homefood/          # Main Django project
├── apps/              # Django applications
│   ├── accounts/      # User authentication & profiles
│   ├── cooks/         # Cook module
│   ├── buyers/        # Buyer module
│   ├── admin_panel/   # Admin module
│   ├── payments/      # Razorpay integration
│   ├── ml_engine/     # ML models
│   └── notifications/ # MSG91 integration
├── static/            # Static files
├── media/             # User uploaded files
└── templates/         # HTML templates
```

## Environment Variables

See `.env.example` for required environment variables.






