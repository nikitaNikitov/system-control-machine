"""
Модуль для классов форм для упрощенной
валидации POST запросов
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterUserForm(UserCreationForm):
	"""
    Форма регистрации
    """

	class Meta:
		"""
		Класс объявление полей, которые связаны с моделью
		"""
		model = CustomUser
		fields = (
			'username', 'first_name', 'last_name', 'middle_name', 'group', 'password1', 'password2'
		)
		widgets = {
			'username': forms.TextInput({'placeholder': 'Никнейм'}),
			'first_name': forms.TextInput({'placeholder': 'Имя'}),
			'last_name': forms.TextInput({'placeholder': 'Фамилия'}),
			'middle_name': forms.TextInput({'placeholder': 'Отчество'}),
			'group': forms.TextInput({'placeholder': 'Группа'}),
		}
		labels = {
			'comment': '',
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Пароль'})
		self.fields['password2'].widget = forms.PasswordInput(
			attrs={'placeholder': 'Подтверждение пароля'}
		)
