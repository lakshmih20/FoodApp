# Review System - Quick Reference Guide

## 🔗 URL Routes

### Review-Related Endpoints

| Endpoint | Method | Purpose | Requires Auth | Parameters |
|----------|--------|---------|---------------|------------|
| `/buyers/orders/` | GET | List all buyer's orders | ✅ Yes | `status` (optional) - filter by status |
| `/buyers/orders/<id>/` | GET | View order details | ✅ Yes | `id` - Order ID |
| `/buyers/orders/<id>/review/` | GET | Review form page | ✅ Yes | `id` - Order ID |
| `/buyers/orders/<id>/review/` | POST | Submit review | ✅ Yes | Form data (see below) |

---

## 📋 Form Data Fields

### Review Submission Form

```
POST /buyers/orders/<id>/review/

Form Fields (multipart/form-data):
├── overall_rating*          [Integer: 1-5] REQUIRED
├── freshness_rating         [Integer: 1-5] Optional
├── hygiene_rating           [Integer: 1-5] Optional
├── taste_rating             [Integer: 1-5] Optional
├── packaging_rating         [Integer: 1-5] Optional
├── comment                  [Text, max 1000 chars] Optional
├── food_photo               [File: image/*] Optional
└── csrfmiddlewaretoken*     [String] REQUIRED

* = Required fields
```

---

## ✅ Review Eligibility Checklist

Before a customer can submit a review:

- [ ] User is logged in
- [ ] User owns the order (order.buyer == request.user)
- [ ] Order exists (order.id exists in database)
- [ ] Order status is "completed" (order.status == 'completed')
- [ ] No review exists for this order yet (BuyerReview not already created)

**If any condition fails:** Error message displayed, review form not allowed.

---

## 🎯 Review Status Flow

```
Order Created (status: pending)
        ↓
Order Accepted (status: accepted)
        ↓
Preparing (status: preparing)
        ↓
Ready for Pickup (status: ready)
        ↓
✅ Completed (status: completed)
        ↓
🟢 REVIEW ALLOWED HERE
```

---

## 📊 Database Schema

### BuyerReview Table
```sql
buyerreview (
    id              INTEGER PRIMARY KEY,
    order_id        INTEGER UNIQUE (FK to BuyerOrder),
    overall_rating  INTEGER (1-5),
    freshness_rating    INTEGER (1-5, nullable),
    hygiene_rating      INTEGER (1-5, nullable),
    taste_rating        INTEGER (1-5, nullable),
    packaging_rating    INTEGER (1-5, nullable),
    comment             TEXT (max 1000 chars),
    food_photo          VARCHAR (file path),
    sentiment_score     DECIMAL (0-1, nullable),
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP (auto)
)
```

---

## 🎨 Template Navigation

```
Order List Page (orders/)
        ↓
Order Detail Page (orders/<id>/)
        ↓
[Status Check]
        ├─→ If Completed ✅
        │   └─→ "Add Your Review" Button Visible
        │       ↓
        │   Review Form Page (orders/<id>/review/)
        │       ↓
        │   [Submit Form]
        │       ↓
        │   Review Stored ✓
        │       ↓
        │   Success Message → Back to Order Detail
        │
        └─→ If Not Completed ⏳
            └─→ "Review available after order completion" Info Message
```

---

## 🔍 Review Access Control

### Who can add a review?
- ✅ Authenticated buyers
- ✅ Who own the order
- ✅ Where order status is "completed"
- ✅ Where no review already exists

### Who cannot add a review?
- ❌ Anonymous/logged out users
- ❌ Buyers who don't own the order
- ❌ Who order is still pending/preparing
- ❌ If review already submitted for order

---

## 📝 Form Validation Rules

### Overall Rating (Required)
- Must select a value
- Must be 1-5
- Error: "Overall rating is required"

### Questionnaire Fields (Optional)
- If provided, must be 1-5
- Can all be left blank
- Each has 5 descriptive options

### Comment (Optional)
- If provided, minimum 10 characters
- Maximum 1000 characters
- Error: "Please provide at least 10 characters"

### Food Photo (Optional)
- Maximum file size: 5 MB
- Allowed formats: JPG, JPEG, PNG, GIF, WebP
- Error: "Photo file size must be less than 5MB"
- Error: "Invalid image format"

---

## 🔔 Events Triggered After Review Submission

1. **Data Saved**
   - BuyerReview record created
   - food_photo saved to media/review_food_photos/

2. **Sentiment Analysis** (Async)
   - Comment text analyzed
   - Sentiment score (0-1) calculated
   - Result stored in BuyerReview

3. **CookReview Created**
   - Mirror review created for cook profile
   - Linked to CookOrder

4. **Cook Rating Updated**
   ```
   New Rating = Average(all CookReview.rating for this cook)
   Total Reviews = Count(all CookReview for this cook)
   ```

5. **User Feedback**
   - Success message: "Review submitted successfully!"
   - Redirect to order detail page

---

## 🛠️ Developer Commands

### Test Review System

```python
# Django Shell
python manage.py shell

# Check if review exists for order
from apps.buyers.models import BuyerReview, BuyerOrder
order = BuyerOrder.objects.get(id=1)
review_exists = BuyerReview.objects.filter(order=order).exists()

# View review details
review = BuyerReview.objects.get(order=order)
print(f"Rating: {review.overall_rating}")
print(f"Comment: {review.comment}")
print(f"Photo: {review.food_photo}")

# Check cook rating
from apps.accounts.models import CookProfile
cook = CookProfile.objects.get(id=1)
print(f"Cook Rating: {cook.rating}")
print(f"Total Reviews: {cook.total_reviews}")

# Find all reviews
all_reviews = BuyerReview.objects.all().order_by('-created_at')
for review in all_reviews:
    print(f"Order #{review.order.id}: {review.overall_rating} stars")
```

---

## 📈 Analytics Queries

### Get Average Rating per Cook
```python
from django.db.models import Avg, Count
from apps.cooks.models import CookReview

ratings = CookReview.objects.values('order__meal__cook').annotate(
    avg_rating=Avg('rating'),
    total=Count('id')
)
```

### Get Recent Reviews
```python
from apps.buyers.models import BuyerReview

recent = BuyerReview.objects.all().order_by('-created_at')[:10]
for review in recent:
    print(f"Order: {review.order}, Rating: {review.overall_rating}, Sentiment: {review.sentiment_score}")
```

### Get High Sentiment Reviews
```python
positive_reviews = BuyerReview.objects.filter(sentiment_score__gte=0.7)
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Add Review" button doesn't show | Order not completed | Wait for order completion |
| Form won't submit | Overall rating not selected | Select a rating |
| "File too large" error | Photo > 5MB | Use smaller image |
| "Invalid format" error | Wrong file type | Use JPG, PNG, GIF, or WebP |
| "Must provide 10+ chars" | Comment too short | Write longer comment |
| Review doesn't save | Form validation error | Check error messages |

---

## 📞 Support Resources

- **Admin Panel:** `/admin/` - View all reviews
- **Django Shell:** `python manage.py shell` - Debug queries
- **Logs:** Check Django error logs for exceptions
- **Documentation:** See REVIEW_SYSTEM_GUIDE.md for detailed info

---

## 🚀 Performance Tips

1. **Photo Optimization:** Compress images before uploading
2. **Sentiment Analysis:** Runs asynchronously to not block submission
3. **Caching:** Cook ratings cached in CookProfile model
4. **Indexing:** Database indexes on order_id and created_at

---

## 📋 Checklist for Testing

- [ ] User cannot add review if order not completed
- [ ] User cannot add review for another user's order
- [ ] Overall rating is required
- [ ] Optional fields can be left blank
- [ ] Photo upload works with valid formats
- [ ] Photo upload rejects invalid formats
- [ ] Comment must be 10+ characters if provided
- [ ] Duplicate reviews prevented
- [ ] Cook rating updates after review
- [ ] Sentiment score calculated
- [ ] Success message displayed
- [ ] Review appears on cook profile
- [ ] Review appears on meal detail page

---

**Last Updated:** January 29, 2026
