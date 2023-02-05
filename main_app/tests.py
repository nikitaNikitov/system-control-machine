"""
Модуль для тестирования приложения перед выпуском в гитлаб
"""
from django.test import Client, TestCase

# Create your tests here.
class IndexTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_get_index_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)