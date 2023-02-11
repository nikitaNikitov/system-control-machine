"""Модуль для создания логики отрисовки страниц"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomUser, RegisterUserForm


@login_required()
def index_page(request):
	"""Возвращает отрисовку главной страницы"""
	return render(request, 'index.html')


def login_user(request):
	"""
	Функция авторизации пользователя

	Если запрос 'POST', проверяет данные и авторизует пользователя
	Иначе отрисовывает страницу авторизации
	"""
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('/')
		messages.error(request, 'Неверный логин или пароль!')
		return render(request, 'auth.html')
	return render(request, 'auth.html')


def register_user(request):
	"""
	Функция регистрации пользователя

	Если запрос 'POST' и форма валидная, то регистрируем страницу
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


def logout_user(request):
	"""Функция разлогинивания пользователя"""
	logout(request)
	return redirect('/')


def profile(request):
	"""
	Функция отрисовки страницы профиля для пользователя

	Отрисовывает страницу профиля с информацией о пользователе
	"""
	user = CustomUser.objects.filter(username=request.user).first()
	if user is None:
		messages.warning(request, "Пользователь не найден!")
		return render(request, 'profile.html')

	form = {
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'middle_name': user.middle_name,
		'group': user.group,
		'status': user.status,
	}
	return render(request, 'profile.html', form)
