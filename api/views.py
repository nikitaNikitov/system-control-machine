"""
Модуль для создания различных методов API
"""
from time import time
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from main_app.models import CustomUser, Machine, Perm, QRCode, generate_access_token

from . import utils


@csrf_exempt
def get_user_from_code(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отображения данных о пользователе через QR код.
	"""
	data = get_user_from_code_handler(request)
	if isinstance(data, JsonResponse):
		return data
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def get_user_from_code_handler(request: WSGIRequest):
	"""
	Функция для получения данных о пользователе через QR код.
	"""
	params = utils.get_params(request)

	if 'code' not in params:
		data = {'error': 110, 'error_msg': '\'code\' argument is missing'}
		return JsonResponse(data)

	machine: Machine | JsonResponse = get_machine_from_token(request)
	if isinstance(machine, JsonResponse):
		return machine

	code = params['code']
	now = time()

	user_object = QRCode.objects.filter(code=code).first()
	data = {}
	if user_object is None:
		data = {'error': 102, 'error_msg': 'Code is not found'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if now < user_object.time_start.timestamp():
		data = {'error': 103, 'error_msg': 'Code is not yet valid'}
	if now > user_object.time_expire.timestamp():
		data = {'error': 104, 'error_msg': 'Code is expired'}
	if len(data) > 0:
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	user: CustomUser = user_object.user

	print(Perm.objects.filter(users=user))

	data = {
		'username':
			user.username,
		'fullname':
			f'{user.last_name} {user.first_name} {user.middle_name}',
		'group':
			user.group,
		'access':
			CustomUser.objects.filter(perms__in=[machine.id], username=user.username).exists(),
	}
	return data


def get_machine_from_token(request: WSGIRequest) -> JsonResponse | Machine:
	"""
	Метод, который получает станок из Bearer токена
	"""
	authorization = request.headers.get('Authorization', None)
	if authorization is None:
		data = {'error': 20, 'error_msg': 'Token not sent'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=401)
	key, token = authorization.split()
	key = key.lower()
	if key.find('bearer') < 0 and key.find('token') < 0:
		data = {'error': 20, 'error_msg': 'Token not sent'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=401)
	machine = Machine.objects.filter(access_token=token).first()
	if machine is None:
		data = {'error': 21, 'error_msg': 'Token is not valid'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, status=401)
	return machine


@login_required
def get_qr(request: WSGIRequest) -> HttpResponse:
	"""
	Функция получеиие QR кода для пользователя
	"""
	user = check_user(request, is_teacher=False)
	if isinstance(user, JsonResponse):
		return user

	return JsonResponse(QRCode.generate_code(user), json_dumps_params={'ensure_ascii': False})


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


@login_required
def manage(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отображение студентов из базы данных по запросу
	"""
	response = manage_handler(request)
	if isinstance(response, JsonResponse):
		return response

	return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


@login_required
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
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)

	response = get_query_params(params)
	if isinstance(response, JsonResponse):
		return response

	query, page_list, limit = response

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

			machines = []
			for i in Perm.objects.filter(users=query_user):
				machines.append(i.machine.short_name)
			users[query_user.username] = {
				'fullname':
					f'{query_user.last_name} {query_user.first_name} {query_user.middle_name}',
				'group':
					query_user.group,
				'data':
					', '.join(machines),
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
	Функция, которая выдает право пльзователю/ям на станок
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)
	data: dict = {}
	if 'user' not in params:
		data = {'error': 110, 'error_msg': '\'user\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if 'machine_id' not in params:
		data = {'error': 110, 'error_msg': '\'machine_id\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	users: list[str] = params.getlist('user')
	machine_id = str(params['machine_id'])

	data = give_permission_users(machine_id, users)

	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def give_permission_users(machine_id: str, users: list[str]) -> dict[str, Any]:
	"""
	Функция, которая записывает в бд информацию о доступе к станку
	"""
	machine = Machine.objects.filter(id=machine_id).first()
	if machine is None:
		return {'error': 13, 'error_msg': f'Machine \'{machine_id}\' is not found'}
	error_users: list[str] = []
	success = False
	for user in users:
		query_user = CustomUser.objects.filter(username=user).first()
		if query_user is None:
			error_users.append(user)
			continue
		permission = Perm.objects.filter(machine=machine).first()
		if permission is None:
			permission = Perm(machine=machine)
			permission.save()
		permission.users.add(query_user)
		success = True
	if not success:
		return {
			'error': 14,
			'error_msg': 'Users were not granted rights because they were not found'
		}
	data = {'success': True, 'success_msg': 'Users have been granted rights'}
	if len(error_users) > 0:
		data['warn'] = True
		data['warn_msg'] = 'Некоторым пользователям не выданы права: ' + ' '.join(error_users)
	return data


@login_required
def revoke_permission(request: WSGIRequest) -> JsonResponse:
	"""
	Функция, которая забирает право пльзователю/ям на станок
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)
	data: dict = {}
	if 'user' not in params:
		data = {'error': 110, 'error_msg': '\'user\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if 'machine_id' not in params:
		data = {'error': 110, 'error_msg': '\'machine_id\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	users: list[str] = params.getlist('user')
	machine_id = str(params['machine_id'])

	data = revoke_permission_users(machine_id, users)

	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def revoke_permission_users(machine_id: str, users: list[str]) -> dict[str, Any]:
	"""
	Функция, которая записывает в бд информацию о доступе к станку
	"""
	machine = Machine.objects.filter(id=machine_id).first()
	if machine is None:
		return {'error': 13, 'error_msg': 'Machine is not found'}
	error_users: list[str] = []
	success = False
	for user in users:
		query_user = CustomUser.objects.filter(username=user).first()
		if query_user is None:
			error_users.append(user)
			continue
		permission = Perm.objects.filter(machine=machine).first()
		if permission is None:
			permission = Perm(machine=machine)
			permission.save()
		permission.users.remove(query_user)
		success = True
	if not success:
		return {
			'error': 14,
			'error_msg': 'Users were not revoked rights because they were not found'
		}
	data = {'success': True, 'success_msg': 'Users have been revoked rights'}
	if len(error_users) > 0:
		data['warn'] = True
		data['warn_msg'] = 'Некоторым пользователям не выданы права: ' + ' '.join(error_users)
	return data


@login_required
def show_machines(request: WSGIRequest) -> JsonResponse:
	"""
	Функция получения станков из базы данных по запросу
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)

	response = get_query_params(params)
	if isinstance(response, JsonResponse):
		return response

	query, page_list, limit = response

	query_set = Machine.search_query(query, limit, page_list)
	machines = {}
	if 'machines' in query_set:
		for machine in query_set['machines']:
			if not isinstance(machine, Machine):
				continue
			machines[machine.id] = {
				'short_name': machine.short_name,
				'description': machine.description,
			}

	data = {
		'max_pages': query_set['max_pages'],
		'current_page': query_set['current_page'],
		'machines': machines,
	}

	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


@login_required
def add_machine(request: WSGIRequest) -> JsonResponse:
	"""
	Функция получения студентов из базы данных по запросу
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)

	machine_id: str = ''
	machine_short_name: str = ''
	machine_description: str = params.get('machine_description', '')
	machine_access_token: str = utils.generate_random_string(64)

	if 'machine_id' not in params:
		data = {'error': 110, 'error_msg': '\'machine_id\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if 'machine_short_name' not in params:
		data = {'error': 110, 'error_msg': '\'machine_short_name\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	machine_id = str(params['machine_id'])
	machine_short_name = str(params['machine_short_name'])

	if 'machine_access_token' in params and len(params['machine_access_token']) > 0:
		machine_access_token = str(params['machine_access_token'])

	return add_machine_handler(
		machine_id, machine_short_name, machine_description, machine_access_token
	)


def add_machine_handler(
	machine_id: str, machine_short_name: str, machine_description: str, machine_access_token: str
) -> JsonResponse:
	"""
	Метод добавления станка в базу данных
	"""
	if Machine.objects.filter(id=machine_id).exists():
		data = {'error': 113, 'error_msg': f'Machine with id \'{machine_id}\' is exists'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if Machine.objects.filter(short_name=machine_short_name).exists():
		data = {
			'error': 113,
			'error_msg': f'Machine with short_name \'{machine_short_name}\' is exists'
		}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	if Machine.objects.filter(access_token=machine_access_token).exists():
		data = {
			'error': 113,
			'error_msg': f'Machine with access_token \'{machine_access_token}\' is exists'
		}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	machine = Machine(
		id=machine_id,
		short_name=machine_short_name,
		description=machine_description,
		access_token=machine_access_token
	)
	machine.save()

	data = {
		'success': True,
		'success_msg': 'Machine is added',
		'access_token': machine.access_token
	}
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def get_query_params(params: QueryDict) -> JsonResponse | tuple[str, int, int]:
	"""
	Функция получение параметров для использования в таблицах для поиска
	[строка, страница, количество записей в одной странице]
	"""
	query = params.get('query', '')
	page_list: int = 1
	limit: int = 10
	if 'limit' in params:
		try:
			limit = int(str(params['limit']))
		except ValueError:
			data = {'error': 111, 'error_msg': 'Argument \'limit\' is not a number'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		if limit < 1:
			data = {'error': 112, 'error_msg': 'Argument \'limit\' cannot be less than one'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		limit = min(limit, 1000)
	if 'list' in params:
		try:
			page_list = int(str(params['list']))
		except ValueError:
			data = {'error': 111, 'error_msg': 'Argument \'list\' is not a number'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		if page_list < 1:
			data = {'error': 112, 'error_msg': 'Argument \'list\' cannot be less than one'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	return query, page_list, limit


@login_required
def delete_machine(request: WSGIRequest) -> JsonResponse:
	"""
	Функция получения студентов из базы данных по запросу
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)
	if 'machine' not in params:
		data = {'error': 110, 'error_msg': '\'machine\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	for machine in params.getlist('machine'):
		Machine.objects.filter(id=machine).delete()

	data = {'success': True, 'success_msg': 'Machine(s) is removed'}
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def regenerate_machine_token_handler(machine: Machine, token: str | None) -> JsonResponse:
	if token is None:
		for _ in range(100):
			token = generate_access_token()
			if not Machine.objects.filter(access_token=token).exists():
				break
		else:
			data = {
				'error': 1,
				'error_msg': 'Failed to generate a token that is different from other machines'
			}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
	elif isinstance(token, str):
		if len(token) < 6:
			data = {
				'error': 114,
				'error_msg': 'Token is too short, which is inconsistent with security'
			}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

		if not utils.is_token(token):
			data = {
				'error': 114,
				'error_msg': 'Token must consist of english characters and numbers only'
			}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
		if Machine.objects.filter(access_token=token).exists():
			data = {'error': 113, 'error_msg': f'Machine with access_token \'{token}\' is exists'}
			return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	machine.access_token = token
	machine.save()

	data = {
		'success': True,
		'success_msg': 'Machine token is succeful regenerate',
		'access_token': token
	}
	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


@login_required
def regenerate_machine_token(request: WSGIRequest) -> JsonResponse:
	"""
	Функция пересоздания токена станка
	"""
	user = check_user(request, is_teacher=True)
	if isinstance(user, JsonResponse):
		return user

	params = utils.get_params(request)
	if 'machine' not in params:
		data = {'error': 110, 'error_msg': '\'machine\' argument is missing'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	machine_id = params['machine']
	machine = Machine.objects.filter(id=machine_id).first()
	if machine is None:
		data = {'error': 13, 'error_msg': f'Machine \'{machine_id}\' is not found'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	token = None
	if 'token' in params:
		token = params['token']

	if token is not None and not isinstance(token, str):
		data = {'error': 114, 'error_msg': 'Argument is not string type'}
		return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

	return regenerate_machine_token_handler(machine, token)


@login_required
def accesses(request: WSGIRequest) -> JsonResponse:
	"""
	Функция отображения списка доступных станков
	"""
	user = check_user(request, False)
	if isinstance(user, HttpResponse):
		return user

	data = {}
	for i in Perm.objects.filter(users=user):
		data[i.machine.id] = {
			'short_name': i.machine.short_name,
			'description': i.machine.description
		}

	return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
