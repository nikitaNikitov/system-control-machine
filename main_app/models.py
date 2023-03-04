"""
Модуль для создании моделей для базы данных
"""
import math

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

STATUSES = (('Student', 'Студент'), ('Teacher', 'Преподаватель'))


class CustomUser(AbstractUser):
	"""
	Класс для создания дополнительных столбцов в базе данных User
	"""

	middle_name = models.CharField(max_length=150, verbose_name='Отчество')
	group = models.CharField(max_length=25, blank=True, verbose_name='Группа')

	status = models.CharField(
		max_length=7, choices=STATUSES, default='Student', verbose_name='Статус'
	)

	data = models.JSONField(blank=False, default=dict, verbose_name='Информация')

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

	@staticmethod
	def search_query(query: str | None, limit: int, page_list: int = 1):
		"""
		Функция поиска в базе данных CustomUser
		"""

		if query is None or len(query) == 0:
			result = CustomUser.objects.all()
		else:
			query_parts = query.split()
			filter_word = query_parts.pop(0)
			result = CustomUser.objects.filter(
				Q(last_name__iregex=filter_word) | Q(first_name__iregex=filter_word) |
				Q(middle_name__iregex=filter_word) | Q(group__iregex=filter_word)
			)

			for i in query_parts:
				result = result.filter(
					Q(last_name__iregex=i) | Q(first_name__iregex=i) | Q(middle_name__iregex=i) |
					Q(group__iregex=i)
				)

		max_pages = math.ceil(len(result) / limit)
		if max_pages < page_list:
			page_list = max(max_pages, 1)

		start = limit * (page_list - 1)
		end = limit + limit * (page_list - 1)
		data = {
			'max_pages': math.ceil(len(result) / limit),
			'current_page': page_list,
			'users': result[start:end]
		}
		return data


class QRCode(models.Model):
	"""
	Таблица с QR кодами пользователей
	"""
	user = models.OneToOneField(
		CustomUser, on_delete=models.CASCADE, primary_key=True, verbose_name="Пользователь"
	)
	code = models.CharField(max_length=16, unique=True, verbose_name="Код")
	time_start = models.DateTimeField(verbose_name="Срок начала действия кода")
	time_expire = models.DateTimeField(verbose_name="Срок истечения действия кода")

	class Meta:
		verbose_name = "QR Код"
		verbose_name_plural = "QR Коды"

	def __str__(self) -> str:
		return f'{self.user} - {self.code}'
