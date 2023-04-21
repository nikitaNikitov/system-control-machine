"""
Модуль для создания логики отрисовки страниц
"""
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render

from api import utils

from .forms import RegisterUserForm
from .models import CustomUser, Perm, QRCode


def check_user(request: WSGIRequest, is_teacher: bool = False) -> HttpResponse | CustomUser:
	"""
	Функция проверки, есть ли пользователь в базе данных и дополнительные проверки пользователя
	"""
	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		messages.warning(request, utils.Error.USER_NOT_FOUND.value)
		return render(request, 'error.html', status=401)

	if is_teacher and not user.is_teacher():
		messages.error(request, utils.Error.USER_NOT_TEACHER.value)
		return render(request, 'error.html', status=403)
	return user


@login_required()
def index_page(request: WSGIRequest) -> HttpResponse:
	"""
	Возвращает отрисовку главной страницы
	"""
	return render(request, 'index.html')


def login_user(
	request: WSGIRequest
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
	"""
	Функция авторизации пользователя

	Если запрос 'POST', проверяет данные и авторизует пользователя
	Иначе отрисовывает страницу авторизации
	"""
	next_page: str | None = request.GET.get('next')
	if next_page is None:
		next_page = '/'

	if request.user.is_authenticated:
		return redirect(next_page)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect(next_page)

		messages.error(request, 'Неверный логин или пароль!')
		return render(request, 'auth.html')

	return render(request, 'auth.html')


def register_user(
	request: WSGIRequest
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
	"""
	Функция регистрации пользователя

	Если запрос 'POST' и форма валидная, то регистрируем страницу
	и переадресовываем на страничку авторизации
	Иначе отрисовывает страницу регистрации
	"""
	if request.method == 'POST':
		form = RegisterUserForm(request.POST)
		if form.is_valid():
			user: CustomUser = form.save(commit=False)
			user.save()
			return redirect('/login/')
	else:
		form = RegisterUserForm()
	return render(request, 'signup.html', {'form': form})


def logout_user(request: WSGIRequest) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
	"""Функция разлогинивания пользователя"""
	logout(request)
	return redirect('login')


@login_required()
def profile(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отрисовки страницы профиля для пользователя

	Отрисовывает страницу профиля с информацией о пользователе
	"""
	return profile_username(request=request, username=request.user.get_username())


@login_required()
def profile_username(request: WSGIRequest, username: str) -> HttpResponse:
	"""
	Функция отрисовки страницы профиля для пользователя

	Отрисовывает страницу профиля с информацией о пользователе
	"""
	user = CustomUser.objects.filter(username=username).first()
	if user is None:
		messages.warning(request, utils.Error.USER_NOT_FOUND.value)
		return render(request, 'profile.html')

	form = {
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'middle_name': user.middle_name,
		'group': user.group,
		'status': user.status_display(),
	}
	return render(request, 'profile.html', form)


@login_required()
def generate_qr(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отрисовки QR кода для пользователя

	Отрисовывает страницу и генерирует QR код для пользователя
	"""

	html_file = 'qr.html'

	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		messages.warning(request, utils.Error.USER_NOT_FOUND.value)
		return render(request, html_file)

	data = QRCode.generate_code(user)
	return render(request, html_file, data)


@login_required()
def manage(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отрисовки меню управления студентами

	Отрисовывает страницу с поиском и таблицей зарегестрированных студентов
	"""

	user = check_user(request, True)
	if isinstance(user, HttpResponse):
		return user

	form: dict[str, Any] = {
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'middle_name': user.middle_name,
		'group': user.group,
		'status': user.status_display(),
	}
	return render(request, 'manage.html', form)


@login_required()
def machines(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отрисовки меню управления станками

	Отрисовывает страницу с поиском и таблицей зарегестрированных станков
	"""

	user = check_user(request, True)
	if isinstance(user, HttpResponse):
		return user

	form: dict[str, Any] = {
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'middle_name': user.middle_name,
		'group': user.group,
		'status': user.status_display(),
	}
	return render(request, 'machines.html', form)


@login_required()
def accesses(request: WSGIRequest) -> HttpResponse:
	"""
	Функция отрисовки страницы с информацией о доступе к станкам

	Отрисовывает страницу со списком станков, к которым пользователь имеет доступ
	"""

	user = check_user(request, False)
	if isinstance(user, HttpResponse):
		return user

	machines_access = []
	for i in Perm.objects.filter(users=user):
		machines_access.append(i.machine.short_name)

	form: dict[str, Any] = {
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'middle_name': user.middle_name,
		'group': user.group,
		'status': user.status_display(),
		'machines': machines_access,
	}
	return render(request, 'accesses.html', form)
