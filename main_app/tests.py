"""Модуль для тестирования приложения"""
from django.test import Client, TestCase


# Create your tests here.
class IndexTest(TestCase):
	"""
	Класс для создания тестов
	"""

	def setUp(self) -> None:
		"""
		Функция инициализации

		Создает перед тестом клиента, который может получать/отправлять GET/POST запросы
		"""
		self.client = Client()

	def test_get_index_endpoint(self) -> None:
		"""
		Тест на доступность страницы
		"""
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
