"""
Модуль для конфигурации приложения
"""
from django.apps import AppConfig


class MainAppConfig(AppConfig):
    """
    Основной класс конфига, где проводится все настройки
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'
