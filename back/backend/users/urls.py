from django.urls import path
from .views import UserCreateView, MessageView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('message/', MessageView.as_view(), name='message'),
]
