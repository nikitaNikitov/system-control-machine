"""
Модуль для создания логики отрисовки страниц
"""
import datetime
import secrets
import string
from time import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import RegisterUserForm
from .models import CustomUser, QRCode

SYMBVOLS = string.ascii_letters + string.digits


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
			user = form.save(commit=False)
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
	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		messages.warning(request, 'Пользователь не найден!')
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
def generate_qr(request: WSGIRequest):
	"""
	Функция отрисовки QR кода для пользователя

	Отрисовывает страницу и генерирует QR код для пользователя
	"""

	html_file = 'qr.html'

	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		messages.warning(request, 'Пользователь не найден!')
		return render(request, html_file)

	usercode = QRCode.objects.filter(user=user).first()
	if usercode is not None:
		if usercode.time_expire.timestamp() - time() > 0:
			form = {
				'code': usercode.code,
				'time_start': int(usercode.time_start.timestamp()),
				'time_expire': int(usercode.time_expire.timestamp()),
			}
			return render(request, html_file, form)

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

	form = {
		'code': code,
		'time_start': int(time_start.timestamp()),
		'time_expire': int(time_expire.timestamp()),
	}
	return render(request, html_file, form)
