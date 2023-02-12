"""
Модуль для создании моделей для базы данных
"""
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

STATUSES = (('Student', 'Студент'), ('Teacher', 'Преподаватель'))


class CustomUser(AbstractUser):
	"""
	Класс для создания дополнительных столбцов в базе данных User
	"""

	middle_name = models.CharField(max_length=50, verbose_name='Отчество')
	group = models.CharField(max_length=25, blank=True, verbose_name='Группа')

	status = models.CharField(
		max_length=7, choices=STATUSES, default='Student', verbose_name='Статус'
	)
	permissions = models.JSONField(blank=True, default=dict, verbose_name='Права')

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

	def status_display(self) -> str:
		"""
		Функция, которая возращает статус студента в
		текстовом виде для отображения
		"""
		return self.get_status_display()  # type: ignore # Рантайм функция от Django


class QRCode(models.Model):
	"""
	Таблица с QR кодами пользователей
	"""
	user = models.OneToOneField(
		CustomUser, on_delete=models.CASCADE, primary_key=True, verbose_name="Пользователь"
	)
	code = models.CharField(max_length=16, unique=True, verbose_name="Код")
	time_start = models.DateTimeField(verbose_name="Срок начала действия кода")
	time_expire = models.DateTimeField(
		default=datetime.now(), verbose_name="Срок истечения действия кода"
	)

	class Meta:
		verbose_name = "QR Код"
		verbose_name_plural = "QR Коды"

	def __str__(self) -> str:
		return f'{self.user} - {self.code}'
