from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chathub/<uuid:chat_channel_uuid>/', views.chat_interface, name='chat_interface'),
    path('create_chat_channel/', views.create_chat_channel_button, name='create_chat_channel'),
    path('chathub/<uuid:chat_uuid>/delete_chat/', views.delete_chat, name='delete_chat'),
]
