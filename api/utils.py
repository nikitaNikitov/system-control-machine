"""
Модуль различных утилит для использования в коде
"""
import datetime
import secrets
import string
from time import time
from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict

from main_app.models import QRCode

SYMBVOLS = string.ascii_letters + string.digits


def get_params(request: WSGIRequest) -> QueryDict:
	"""
	Метод для получение аргументов в запросе

	Если запрос: POST, получает аргументы оттуда
	Иначе: получает аргументы из GET
	"""
	if request.POST:
		return request.POST
	return request.GET


def generate_code(user) -> dict[str, Any]:
	"""
	Создает JSON с кодом, время начала и конца действия
	"""
	data: dict[str, Any] = {}
	usercode = QRCode.objects.filter(user=user).first()
	if usercode is not None:
		if usercode.time_expire.timestamp() - time() > 0:
			data = {
				'code': usercode.code,
				'time_start': int(usercode.time_start.timestamp()),
				'time_expire': int(usercode.time_expire.timestamp()),
			}
			return data
		usercode.delete()

	code = ''.join(secrets.choice(SYMBVOLS) for _ in range(16))
	time_start = datetime.datetime.now() + datetime.timedelta(seconds=5)
	time_expire = datetime.datetime.now() + datetime.timedelta(minutes=5, seconds=5)

	QRCode(
		user=user,
		code=code,
		time_start=time_start,
		time_expire=time_expire,
	).save()

	data = {
		'code': code,
		'time_start': int(time_start.timestamp()),
		'time_expire': int(time_expire.timestamp()),
	}
	return data
	