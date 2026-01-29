from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from textblob import TextBlob
import pandas as pd
#from prophet import Prophet  # Removed to avoid import error
from apps.accounts.models import User
from apps.cooks.models import Meal, CookOrder, CookReview
from apps.buyers.models import BuyerOrder, BuyerReview, FavoriteCook
from apps.accounts.models import UserProfile
from .models import RecommendationCache, DemandForecast


class RecommendationService:
    """ML-based recommendation service"""
    def get_recommendations(self, user, limit=12):
        """
        Recommend meals to a user based on collaborative filtering (order history).
        """
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        from apps.buyers.models import BuyerOrder
        from apps.cooks.models import Meal
        # Get all users and meals
        users = list(User.objects.all())
        meals = list(Meal.objects.filter(is_available=True))
        if not users or not meals:
            return []
        # Build user-meal matrix (rows: users, cols: meals)
        user_idx = {u.id: i for i, u in enumerate(users)}
        meal_idx = {m.id: i for i, m in enumerate(meals)}
        matrix = np.zeros((len(users), len(meals)))
        # Fill matrix with order counts
        for order in BuyerOrder.objects.filter(meal__in=meals):
            i = user_idx[order.buyer.id]
            j = meal_idx[order.meal.id]
            matrix[i, j] += 1
        # Get current user's vector
        if user.id not in user_idx:
            return list(Meal.objects.filter(is_available=True).order_by('-created_at')[:limit])
        user_vector = matrix[user_idx[user.id]].reshape(1, -1)
        # Compute similarity to other users
        similarities = cosine_similarity(user_vector, matrix)[0]
        # Weighted sum of meals ordered by similar users
        meal_scores = np.dot(similarities, matrix)
        # Exclude meals already ordered by user
        already_ordered = set(BuyerOrder.objects.filter(buyer=user).values_list('meal_id', flat=True))
        meal_score_pairs = [
            (meals[j], score)
            for j, score in enumerate(meal_scores)
            if meals[j].id not in already_ordered
        ]
        # Sort by score
        meal_score_pairs.sort(key=lambda x: x[1], reverse=True)
        recommended_meals = [m for m, s in meal_score_pairs[:limit]]
        # Fallback: fill with latest meals if not enough
        if len(recommended_meals) < limit:
            extra = Meal.objects.filter(is_available=True).exclude(id__in=[m.id for m in recommended_meals]).order_by('-created_at')[:limit-len(recommended_meals)]
            recommended_meals += list(extra)
        return recommended_meals

# ...rest of the file unchanged...
