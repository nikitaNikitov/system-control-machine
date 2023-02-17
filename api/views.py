"""
Модуль для создания различных методов API
"""
from time import time

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from main_app.models import CustomUser, QRCode

from . import utils


@csrf_exempt
def get_user_from_code(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отображения данных о пользователе через QR код.
	"""
	params = utils.get_params(request)

	if 'code' not in params:
		data = {'error': 101, 'error_msg': 'You not receive code'}
		return JsonResponse(data)

	code = params['code']
	now = time()

	user_object = QRCode.objects.filter(code=code).first()
	if user_object is None:
		data = {'error': 102, 'error_msg': 'Code is not found'}
	elif now < user_object.time_start.timestamp():
		data = {'error': 103, 'error_msg': 'Code is not yet valid'}
	elif now > user_object.time_expire.timestamp():
		data = {'error': 104, 'error_msg': 'Code is expired'}
	else:
		user: CustomUser = user_object.user
		data = {
			'username': user.username,
			'fullname': f'{user.last_name} {user.first_name} {user.middle_name}',
			'permissions': user.permissions
		}

	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
