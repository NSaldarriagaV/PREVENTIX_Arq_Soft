from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('calendar/', views.calendar_view, name='calendar'),
]
