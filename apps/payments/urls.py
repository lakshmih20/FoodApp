from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process'),
    path('success/', views.payment_success, name='success'),
    path('failure/', views.payment_failure, name='failure'),
    path('callback/', views.payment_callback, name='callback'),
]






