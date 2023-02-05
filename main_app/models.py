"""
Модуль для создании моделей для базы данных
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

STATUSES = (
    ('Student', 'Студент'),
    ('Teacher', 'Преподаватель')
)

# Create your models here.


class CustomUser(AbstractUser):
    """
    Класс для создания дополнительных столбцов в базе данных User
    """

    middle_name = models.CharField(max_length=50, verbose_name="Отчество")
    group = models.CharField(max_length=25, blank=True, verbose_name="Группа")

    status = models.CharField(
        max_length=7,
        choices=STATUSES,
        default='Student',
        verbose_name="Статус"
    )

    permissions = models.JSONField(
        blank=True, default=dict, verbose_name="Права")

    def is_student(self) -> bool:
        """
        Функция, которая возвращает, является ли
        данный пользователь - студентом
        """
        return self.status == 'Student'

    def is_teacher(self) -> bool:
        """
        Функция, которая возвращает, является ли
        данный пользователь - преподователем
        """
        return self.status == 'Teacher'
