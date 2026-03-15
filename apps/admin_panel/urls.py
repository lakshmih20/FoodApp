from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cooks/verify/', views.cook_verification_list, name='cook_verification_list'),
    path('cooks/<int:cook_id>/review/', views.cook_verification_review, name='cook_verification_review'),
    path('cooks/<int:cook_id>/verify/', views.verify_cook, name='verify_cook_legacy'),
    path('cooks/<int:cook_id>/reject/', views.reject_cook, name='reject_cook_legacy'),
    path('verify/<int:cook_id>/', views.verify_cook, name='verify_cook'),
    path('reject/<int:cook_id>/', views.reject_cook, name='reject_cook'),
    path('users/', views.user_list, name='user_list'),
    path('deactivate/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('orders/', views.order_list, name='order_list'),
    path('disputes/', views.dispute_list, name='dispute_list'),
    path('resolve/<int:report_id>/', views.resolve_dispute, name='resolve_dispute'),
    path('meals/', views.meal_list, name='meal_list'),
    path('unpublish/<int:meal_id>/', views.toggle_meal_publish, name='toggle_meal_publish'),
    path('analytics/', views.dashboard, name='analytics'),
]






