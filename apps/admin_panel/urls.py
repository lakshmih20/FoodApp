from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cooks/verify/', views.cook_verification_list, name='cook_verification_list'),
    path('cooks/<int:cook_id>/verify/', views.verify_cook, name='verify_cook'),
    path('cooks/<int:cook_id>/reject/', views.reject_cook, name='reject_cook'),
    path('users/', views.user_list, name='user_list'),
    path('orders/', views.order_list, name='order_list'),
    path('disputes/', views.dispute_list, name='dispute_list'),
    path('analytics/', views.analytics, name='analytics'),
]






