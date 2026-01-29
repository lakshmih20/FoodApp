from django.urls import path
from . import views

app_name = 'cooks'

urlpatterns = [
    # Cook dashboard and management
    path('dashboard/', views.dashboard, name='dashboard'),
    path('meals/', views.meal_list, name='meals'),
    path('meals/create/', views.meal_create, name='meal_create'),
    path('meals/<int:pk>/edit/', views.meal_edit, name='meal_edit'),
    path('meals/<int:pk>/delete/', views.meal_delete, name='meal_delete'),
    path('meals/<int:meal_id>/slots/', views.pickup_slots, name='pickup_slots'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:pk>/accept/', views.order_accept, name='order_accept'),
    path('orders/<int:pk>/reject/', views.order_reject, name='order_reject'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('analytics/', views.analytics, name='analytics'),
    path('reviews/', views.reviews, name='reviews'),

    # FSSAI certificate upload
    path('fssai-certificate/', views.fssai_certificate_upload, name='fssai_certificate_upload'),

    # Public/buyer APIs
    path('api/nearby/', views.nearby_cooks, name='nearby_cooks'),
    path('api/orders/', views.create_order, name='create_order'),
]
