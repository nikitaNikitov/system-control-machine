"""
Модуль для создания различных методов API
"""
from time import time

from django.http import HttpResponse, JsonResponse

from main_app.models import QRCode


def get_user_from_code(_, code: str) -> HttpResponse:
	"""
	Функция отображения данных о пользователе через QR код.
	"""
	now = time()
	user_object = QRCode.objects.filter(code=code).first()
	if user_object is None:
		data = {'error': 102, 'error_msg': 'Code is not found'}
		return JsonResponse(data)
	if now < user_object.time_start.timestamp():
		data = {'error': 103, 'error_msg': 'Code is not yet valid'}
		return JsonResponse(data)
	if now > user_object.time_expire.timestamp():
		data = {'error': 104, 'error_msg': 'Code is expired'}
		return JsonResponse(data)

	user = user_object.user
	data = {
		'username': user.username,
		'fullname': f'{user.last_name} {user.first_name} {user.middle_name}',
		'permission': user.permissions
	}
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
