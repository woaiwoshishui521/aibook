from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('status/', views.get_service_status, name='status'),
    path('control/', views.ServiceControl.as_view(), name='control'),
    path('', views.ServiceDashboard.as_view(), name='dashboard'),
]
