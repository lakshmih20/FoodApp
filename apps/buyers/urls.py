from django.urls import path
from . import views

app_name = 'buyers'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('meals/<int:pk>/', views.meal_detail, name='meal_detail'),
    path('cook/<int:cook_id>/', views.cook_profile, name='cook_profile'),
    path('order/<int:meal_id>/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/review/', views.add_review, name='add_review'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/add/<int:cook_id>/', views.add_favorite, name='add_favorite'),
    path('recommendations/', views.recommendations, name='recommendations'),

    # Nearby cooks map page
    path('nearby/', views.buyer_nearby, name='buyer_nearby'),

    # API endpoint for location-based filtering
    path('api/nearby-meals/', views.api_nearby_meals, name='api_nearby_meals'),
]
