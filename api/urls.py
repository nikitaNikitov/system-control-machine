"""
Модуль для привязки API url к методам
"""
from django.urls import path

from .views import get_qr, get_user_from_code

urlpatterns = [
	path('getUser', get_user_from_code),
	path('qr', get_qr)
]
