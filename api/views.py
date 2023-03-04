"""
Модуль для создания различных методов API
"""
from time import time
from typing import Any

from django.contrib.auth.decorators import login_required
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
	data = get_user_from_code_handler(request)
	if isinstance(data, JsonResponse):
		return data
	data_field = data.pop('data')
	permissions: dict = {}
	if 'permission' in data_field:
		permissions = data_field['permission']
	data['permissions'] = permissions
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def get_user_from_code_machine(request: WSGIRequest, machine: str) -> HttpResponse:
	"""
	Функция отображения данных о пользователе через QR код.
	"""
	response = get_user_from_code_handler(request)
	if isinstance(response, JsonResponse):
		return response

	data = response.pop('data')
	access = utils.check_access_from_data(data, machine)
	response['access'] = False
	if access is not False:
		response['access'] = True
		response['data'] = access

	return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def get_user_from_code_handler(request: WSGIRequest):
	"""
	Функция для получения данных о пользователе через QR код.
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
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if now < user_object.time_start.timestamp():
		data = {'error': 103, 'error_msg': 'Code is not yet valid'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if now > user_object.time_expire.timestamp():
		data = {'error': 104, 'error_msg': 'Code is expired'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	user: CustomUser = user_object.user
	data = {
		'username': user.username,
		'fullname': f'{user.last_name} {user.first_name} {user.middle_name}',
		'group': user.group,
		'data': user.data,
	}
	return data


@login_required()
def get_qr(request: WSGIRequest) -> HttpResponse:
	"""
	Функция получеиие QR кода для пользователя
	"""
	user = check_user(request, is_teacher=False)
	if isinstance(user, JsonResponse):
		return user

	return JsonResponse(utils.generate_code(user), json_dumps_params={'ensure_ascii': False})


def check_user(
	request: WSGIRequest,
	is_teacher: bool = False,
	is_student: bool = False
) -> JsonResponse | CustomUser:
	"""
	Функция проверки, есть ли пользователь в базе данных и дополнительные проверки пользователя
	"""
	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		data = {'error': 10, 'error_msg': 'User is not found'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=401)
	if is_teacher and not user.is_teacher():
		data = {'error': 11, 'error_msg': 'User is not teacher'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=403)
	if is_student and not user.is_student():
		data = {'error': 12, 'error_msg': 'User is not student'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=403)
	return user


@login_required()
def manage(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отображение студентов из базы данных по запросу
	"""
	response = manage_handler(request)
	if isinstance(response, JsonResponse):
		return response

	return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


@login_required()
def manage_machine(request: WSGIRequest, machine: str) -> HttpResponse:
	"""
	Функция поиска и отображение студентов из базы данных по запросу

	Данная функция может отображать пользователей и их доступ к указаному станку
	"""
	response = manage_handler(request)
	if isinstance(response, JsonResponse):
		return response

	if 'users' in response:
		for query_user in response['users']:
			access = utils.check_access_from_user(query_user, machine)
			response['users'][query_user]['access'] = False
			if access is not False:
				response['users'][query_user]['access'] = True
				response['users'][query_user]['data'] = access

	return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def manage_handler(request: WSGIRequest):
	"""
	Функция получения студентов из базы данных по запросу
	"""
	response = check_user(request, is_teacher=True)
	if isinstance(response, JsonResponse):
		return response

	params = utils.get_params(request)

	query = ''
	page_list: int = 1
	limit: int = 10
	if 'query' in params:
		query = str(params['query'])
	if 'limit' in params:
		try:
			limit = int(str(params['limit']))
		except ValueError:
			data = {'error': 110, 'error_msg': 'Argument \'limit\' is not a number'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		if limit < 1:
			data = {'error': 111, 'error_msg': 'Argument \'limit\' cannot be less than one'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		limit = min(limit, 1000)
	if 'list' in params:
		try:
			page_list = int(str(params['list']))
		except ValueError:
			data = {'error': 110, 'error_msg': 'Argument \'list\' is not a number'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		if page_list < 1:
			data = {'error': 111, 'error_msg': 'Argument \'limit\' cannot be less than one'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	query_set: dict[str, Any] = CustomUser.search_query(query, limit, page_list)
	data = manage_configurate_response_data(query_set)

	return data


def manage_configurate_response_data(query_set):
	"""
	Превращает набор запросов в более удобный вид для страницы
	"""
	users = {}
	if 'users' in query_set:
		for query_user in query_set['users']:
			if not isinstance(query_user, CustomUser):
				continue
			users[query_user.username] = {
				'fullname':
					f'{query_user.last_name} {query_user.first_name} {query_user.middle_name}',
				'group':
					query_user.group,
				'data':
					query_user.data,
			}
	data = {
		'max_pages': query_set['max_pages'],
		'current_page': query_set['current_page'],
		'users': users
	}
	return data


@login_required
def give_permission(request: WSGIRequest) -> JsonResponse:
	"""
	Функция, которая выдает право пльзователю/ям на станок на время от и до
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)
	data: dict = {}
	if 'machine' not in params:
		data = {'error': 121, 'error_msg': '\'machine\' argument is missing'}
	if 'time_end' not in params:
		data = {'error': 122, 'error_msg': '\'time_end\' argument is missing'}
	if 'user' not in params and 'users' not in params:
		data = {'error': 120, 'error_msg': '\'user\' and \'users\' argument is missing'}
	if len(data) > 0:
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	machine = str(params['machine'])

	try:
		time_end: int = int(str(params['time_end']))
	except ValueError:
		data = {'error': 110, 'error_msg': 'Argument \'time_end\' is not a number'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	time_start: int = 0
	if 'time_start' in params:
		try:
			time_start = int(str(params['time_start']))
		except ValueError:
			data = {'error': 110, 'error_msg': 'Argument \'time_start\' is not a number'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	users: list[str] = []
	if 'user' in params:
		users = [str(params['user']).strip()]
	elif 'users' in params:
		users = str(params['users']).strip().split()

	success: dict[str, Any] = give_permission_users(users, machine, user, time_end, time_start)

	return JsonResponse(success, json_dumps_params={'ensure_ascii': False})


def give_permission_users(
	usernames: list[str],
	machine: str,
	who_give: CustomUser,
	time_end: int,
	time_start: int = 0,
	comment: str = ''
) -> dict[str, Any]:
	"""
	Функция, которая записывает в бд информацию о доступе к станку
	"""
	success: dict[str, Any] = {'success': True}
	if not who_give.is_teacher():
		success['success'] = False
		success['error'] = 11
		success['error_msg'] = 'Only the teacher can give a permission'
		return success
	users_error: list[str]
	for user in usernames:
		query_user = CustomUser.objects.filter(username=user).first()
		if not isinstance(query_user, CustomUser):
			success['success'] = False
			users_error = success.setdefault('users_error', [])
			users_error.append(user)
		elif isinstance(query_user.data, dict):
			permission = query_user.data.setdefault('permission', dict)
			permission[machine] = {
				'time_start': time_start,
				'time_end': time_end,
				'who_give': who_give.username,
				'comment': comment
			}
			query_user.save()
	return success
