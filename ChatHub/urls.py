from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chathub/', views.chat_interface, name='ChatInterface'),
]