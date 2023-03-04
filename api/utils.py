"""
Модуль различных утилит для использования в коде
"""
from enum import Enum
import json
import re
import secrets
import string
from time import time
from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict
from django.utils import timezone

from main_app.models import QRCode

SYMBVOLS = string.ascii_letters + string.digits


class Error(Enum):
	"""
	Класс сообщений для ошибок
	"""
	USER_NOT_FOUND = 'Пользователь не найден!'
	USER_NOT_TEACHER = 'Пользователь не является преподавателем!'


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
	time_start = timezone.now() + timezone.timedelta(seconds=5)
	time_expire = timezone.now() + timezone.timedelta(minutes=5, seconds=5)

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


ENGLISH_PATTERN = '[A-z0-9]+'
RUSSIAN_PATTERN = '[А-яЁё]+'


def has_only_english_and_number_letters(name) -> bool:
	"""
	Проверяет, состоит ли строка только из английских букв и цифр
	"""
	return bool(re.fullmatch(ENGLISH_PATTERN, name))


def has_only_russian_letters(name) -> bool:
	"""
	Проверяет, состоит ли строка только из русских букв
	"""
	return bool(re.fullmatch(RUSSIAN_PATTERN, name))


def check_access_from_user(user: dict, machine_name: str) -> bool | dict:
	"""
	Проверяет, есть ли доступ у пользователя к данному станку
	"""
	if 'data' in user:
		return check_access_from_data(json.loads(user['data']), machine_name)
	return False


def check_access_from_data(data: dict, machine_name: str) -> bool | dict:
	"""
	Проверяет, есть ли доступ в информации к данному станку
	"""
	if 'permission' not in data or machine_name not in data['permission']:
		return False
	data = data['permission'][machine_name]
	now = timezone.now().timestamp()
	print(now)
	if data['time_start'] <= now <= data['time_end']:
		return data
	return False
