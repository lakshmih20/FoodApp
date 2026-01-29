# Review & Rating System - Complete Documentation

## Overview
Your FoodApp now has a comprehensive review and rating system that allows customers to share their feedback after completing their meal purchases. The system is designed to be intuitive, secure, and provides valuable insights for both customers and cooks.

---

## ✅ System Features

### 1. **Review Eligibility Validation**
Only buyers who have **successfully completed an order** can submit a review.

**Validation Checks:**
- ✅ Order status must be `completed`
- ✅ Only the buyer who placed the order can review
- ✅ One review per order (duplicate reviews are prevented)
- ✅ Review submission is only available after order is marked as completed

**Location:** [apps/buyers/views.py - add_review function](apps/buyers/views.py#L375-L388)

---

### 2. **Review Components**

#### A. **Overall Star Rating** (1-5 stars)
- Required field
- Single choice rating to represent the overall experience
- Directly impacts cook's profile rating

#### B. **Questionnaire-Based Feedback**
Buyers answer 4 structured questions with 1-5 scale ratings:

**1. Freshness Rating** ❓ "Was the food fresh?"
- 1 star: Poor - Stale/Old
- 2 stars: Fair - Slightly stale
- 3 stars: Good - Fresh
- 4 stars: Very Good - Very Fresh
- 5 stars: Excellent - Extremely Fresh

**2. Hygiene Rating** ❓ "Was the food hygienically packed?"
- 1 star: Poor - Very unsanitary
- 2 stars: Fair - Some hygiene concerns
- 3 stars: Good - Generally hygienic
- 4 stars: Very Good - Very clean
- 5 stars: Excellent - Impeccably clean

**3. Taste Rating** ❓ "Was the taste satisfactory?"
- 1 star: Poor - Inedible
- 2 stars: Fair - Barely edible
- 3 stars: Good - Acceptable taste
- 4 stars: Very Good - Delicious
- 5 stars: Excellent - Exceptional taste

**4. Packaging/Pickup Rating** ❓ "Was the pickup experience smooth?"
- 1 star: Poor - Damaged/leaking
- 2 stars: Fair - Some issues
- 3 stars: Good - Adequate packaging
- 4 stars: Very Good - Well packaged
- 5 stars: Excellent - Premium packaging

#### C. **Text Feedback (Optional)**
- Max 1000 characters
- Minimum 10 characters if provided
- Allows customers to share detailed feedback
- Subject to sentiment analysis

#### D. **Food Photo Upload (Optional)**
- Supports: JPG, JPEG, PNG, GIF, WebP
- Maximum file size: 5MB
- Helps other customers see the actual meal presentation
- Stored in `media/review_food_photos/`

---

## 📊 Advanced Features

### **Sentiment Analysis**
Every review's comment is analyzed for sentiment:
- Sentiment score is calculated and stored (0-1 scale)
- Helps identify patterns in customer satisfaction
- Used for trend analysis and recommendations

**Location:** [apps/ml_engine/ml_services.py - SentimentAnalysisService]

### **Dual Review System**
Both `BuyerReview` and `CookReview` are created:
- **BuyerReview:** Full questionnaire and details from buyer perspective
- **CookReview:** Simpler form for cook to see feedback
- Ensures data consistency across the system

### **Cook Rating Automatic Update**
After each review is submitted:
1. Cook's average rating is recalculated
2. Total review count is updated
3. Rating is used for cook verification and recommendations

**Location:** [apps/buyers/views.py - Line 403-409](apps/buyers/views.py#L403-L409)

---

## 🔄 Review Workflow

### Step 1: Order Completion
```
1. Customer places order → 2. Order accepted → 3. Meal prepared → 4. Pickup complete → 5. Order marked as "Completed"
```

### Step 2: Review Eligibility Check
```
Go to Order Detail Page
    ↓
Check Order Status
    ├─ If Completed → Show "Add Your Review" button ✅
    └─ If Not Completed → Show "Review available after order completion" ℹ️
```

### Step 3: Review Submission
```
1. Click "Add Your Review" button
2. Fill out the review form:
   - Overall rating (required)
   - Questionnaire responses (optional but encouraged)
   - Comments (optional, min 10 chars)
   - Food photo (optional, max 5MB)
3. Click "Submit Review"
4. Review saved and cook's rating updated
```

### Step 4: Post-Submission
```
- Confirmation message displayed
- Review appears on meal/cook profile
- Cook receives notification (if enabled)
- Sentiment analysis runs in background
- Cook's rating updated
```

---

## 📂 Database Models

### **BuyerReview Model**
```python
class BuyerReview(models.Model):
    order = OneToOneField(BuyerOrder)           # Link to order
    overall_rating = IntegerField(1-5)          # Overall rating (required)
    comment = TextField()                       # Customer feedback (optional)
    
    # Questionnaire fields (all optional)
    freshness_rating = IntegerField(1-5)        # Food freshness
    hygiene_rating = IntegerField(1-5)          # Hygiene/packing
    taste_rating = IntegerField(1-5)            # Taste satisfaction
    packaging_rating = IntegerField(1-5)        # Pickup experience
    
    # Media and analytics
    food_photo = ImageField()                   # Food photo (optional)
    sentiment_score = DecimalField(0-1)         # AI sentiment analysis
    created_at = DateTimeField()                # Review submission time
```

**Location:** [apps/buyers/models.py - BuyerReview](apps/buyers/models.py#L46-L99)

---

## 🎨 Frontend Components

### **Order Detail Page** (`buyers/order_detail.html`)
Features:
- Clean order summary display
- Order status badge
- Location details with Google Maps link
- Pickup schedule information
- Prominent review call-to-action for completed orders
- Status-specific messaging

**Key Elements:**
```html
✅ For Completed Orders:
   - Green alert box with "Order Completed!" message
   - Large blue "Add Your Review" button
   - Encouragement message

⏳ For Pending Orders:
   - Info alert with "Review available after order completion"

❌ For Cancelled/Rejected:
   - Red alert showing status
```

### **Add Review Form** (`buyers/add_review.html`)
Features:
- Order summary at top for context
- Organized review form with sections:
  - Overall rating
  - Questionnaire section with 4 questions
  - Comments section
  - Photo upload section
- Clear labeling with icons
- Form validation with error messages
- Info alert about review importance
- Submit and Cancel buttons

**Form Fields:**
```
┌─────────────────────────────────────┐
│ ORDER SUMMARY                       │
│ - Meal name, cook, quantity, price  │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ OVERALL RATING (Required)           │
│ - Star dropdown (1-5)               │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ QUESTIONNAIRE (Optional)            │
│ - Freshness rating                  │
│ - Hygiene rating                    │
│ - Taste rating                      │
│ - Packaging/Pickup rating           │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ COMMENTS (Optional)                 │
│ - Text area (max 1000 chars)        │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ PHOTO UPLOAD (Optional)             │
│ - Image file input (max 5MB)        │
└─────────────────────────────────────┘
        ↓
    [SUBMIT] [CANCEL]
```

---

## 🔐 Security Features

### **Access Control**
- Only authenticated users can submit reviews
- Users can only review their own orders
- `@login_required` decorator on all review views

### **Data Validation**
- Overall rating required
- Photo file size validation (max 5MB)
- Photo format validation (jpg, png, gif, webp only)
- Comment length validation (min 10 chars if provided)
- SQL injection prevention via Django ORM
- CSRF protection on all forms

### **Business Logic Validation**
- Only completed orders can be reviewed
- Duplicate reviews prevented
- Order ownership verified before allowing review

---

## 📝 File Locations

| Component | File Location |
|-----------|---------------|
| **Models** | [apps/buyers/models.py](apps/buyers/models.py#L46) |
| **Views** | [apps/buyers/views.py](apps/buyers/views.py#L375) |
| **Forms** | [apps/buyers/forms.py](apps/buyers/forms.py#L23) |
| **Order Detail Template** | [templates/buyers/order_detail.html](templates/buyers/order_detail.html) |
| **Review Form Template** | [templates/buyers/add_review.html](templates/buyers/add_review.html) |
| **URLs** | [apps/buyers/urls.py](apps/buyers/urls.py) |

---

## 🛠️ Developer Notes

### **URL Endpoints**
```
/buyers/order-list/                    # View all orders
/buyers/order/<id>/                    # View order details
/buyers/order/<id>/add-review/         # Add review form
```

### **Related Models Used**
- `BuyerOrder` - Links review to specific order
- `BuyerReview` - Stores review data
- `CookReview` - Mirror review for cook profile
- `CookProfile` - Updated with new rating after review

### **Signals & Hooks**
- Review submission triggers:
  1. Sentiment analysis (if ML engine enabled)
  2. CookReview creation
  3. Cook rating recalculation
  4. Cook profile update

### **Admin Interface**
- Reviews manageable via Django admin
- Can filter by order, cook, date
- Can search by comment text
- Can view photo uploads

---

## 🚀 Usage Example

### **Complete User Journey**

```
1. BUYER PLACES ORDER
   User: Places order at 2:30 PM on "Butter Chicken" from Cook "Sharma"
   System: Creates BuyerOrder with status="pending"

2. COOK PREPARES MEAL
   Status: pending → accepted → preparing → ready

3. BUYER PICKS UP MEAL
   User: Picks up meal between 6:00 PM - 7:00 PM

4. ORDER MARKED COMPLETED
   Status: ready → completed
   System: "Add Review" button now appears

5. BUYER ADDS REVIEW
   User clicks "Add Your Review"
   ↓
   Form loads with order summary
   ↓
   User fills:
   - Overall Rating: 5 stars ⭐⭐⭐⭐⭐
   - Freshness: 5 (Extremely Fresh) 🌿
   - Hygiene: 5 (Impeccably clean) 🧼
   - Taste: 5 (Exceptional taste) 👌
   - Packaging: 4 (Well packaged) 📦
   - Comment: "Amazing butter chicken! Tasted just like restaurant quality. Would definitely order again!"
   - Photo: [uploads photo of meal]
   ↓
   User clicks "Submit Review"

6. SYSTEM PROCESSES REVIEW
   - Validates all data ✓
   - Stores BuyerReview ✓
   - Analyzes sentiment (Positive: 0.95) ✓
   - Creates CookReview ✓
   - Updates Cook Rating:
     * Previous Rating: 4.2 stars
     * New Rating: 4.5 stars (due to this 5-star review)
   - Updates Cook Total Reviews: 23 → 24 ✓
   - Shows success message ✓

7. REVIEW VISIBLE
   - Appears on meal detail page ✓
   - Appears on cook profile ✓
   - Other buyers can see review with photo ✓
   - Cook can see feedback ✓
```

---

## 📊 Analytics & Reporting

### **Review Statistics Available**
- Total reviews per cook
- Average rating per cook
- Rating distribution (1-5 stars)
- Freshness trend
- Hygiene trend
- Taste trend
- Packaging trend
- Sentiment score distribution
- Reviews with photos
- Reviews with comments

### **Admin Dashboard Integration**
View reviews statistics in admin panel:
- Filters by cook, date range, rating
- Export reviews data
- Monitor for problematic ratings
- Track improvements over time

---

## ⚠️ Troubleshooting

### **Issue: "Add Review" button not showing**
**Causes:**
- Order status is not "Completed"
- User is not logged in
- User is not the order owner

**Solution:** Check order status in order detail page

### **Issue: Review form submission fails**
**Common reasons:**
- Overall rating not selected (required)
- Photo file too large (>5MB)
- Photo format not supported
- Comment too short (<10 chars)

**Solution:** Check form error messages

### **Issue: Photo not uploading**
**Check:**
- File size < 5MB
- File format: JPG, PNG, GIF, WebP
- Browser file upload permissions
- Disk space on server

**Solution:** Try different photo or smaller file

---

## 📞 Support & Maintenance

### **Regular Checks**
- Monitor review submission success rate
- Check sentiment analysis accuracy
- Verify photo storage and cleanup
- Monitor database storage for reviews

### **Future Enhancements**
- Review moderation (flag inappropriate reviews)
- Review response system (cook can respond to reviews)
- Helpful votes (other users vote if review was helpful)
- Review analytics dashboard
- Email notifications for reviews
- Review categories/tags
- Review media gallery with multiple photos

---

## ✨ Best Practices

### **For Buyers**
✅ Write honest and detailed reviews
✅ Include photo of actual meal received
✅ Be respectful and constructive
✅ Mention both positives and areas for improvement
✅ Check before submitting if review is accurate

### **For Cooks**
✅ Monitor customer reviews regularly
✅ Respond to feedback constructively
✅ Maintain high standards consistently
✅ Address negative reviews professionally
✅ Use reviews to improve service

### **For Administrators**
✅ Monitor for fake/spam reviews
✅ Ensure sentiment analysis is working
✅ Regular database backups
✅ Monitor storage for uploaded photos
✅ Provide support to users having issues

---

**Last Updated:** January 29, 2026  
**System Version:** 1.0  
**Status:** ✅ Fully Implemented
