"""
Модуль различных утилит для использования в коде
"""
from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict


def get_params(request: WSGIRequest) -> QueryDict:
	"""
	Метод для получение аргументов в запросе

	Если запрос: POST, получает аргументы оттуда
	Иначе: получает аргументы из GET
	"""
	if request.POST:
		return request.POST
	return request.GET
