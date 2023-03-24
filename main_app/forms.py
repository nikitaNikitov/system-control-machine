"""
Модуль для классов форм для упрощенной
валидации POST запросов
"""
from enum import Enum

from django import forms
from django.contrib.auth.forms import UserCreationForm

from api.utils import (
	ENGLISH_PATTERN,
	RUSSIAN_PATTERN,
	has_only_english_and_number_letters,
	has_only_russian_letters,
)

from .models import CustomUser


class WarningForm(Enum):
	"""
	Сообщения предупреждений для форм
	"""
	USERNAME = 'Имя пользователя должно состоять из английских символов или цифр, без пробелов'
	FIRST_NAME = 'Имя должно состоять из русских символов без пробелов'
	LAST_NAME = 'Фамилия должна состоять из русских символов без пробелов'
	MIDDLE_NAME = 'Отчество должно состоять из русских символов без пробелов'


class RegisterUserForm(UserCreationForm):
	"""
    Форма для регистрации пользователя
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
			'username':
				forms.TextInput({
					'placeholder': 'Никнейм',
					'pattern': ENGLISH_PATTERN,
					'title': WarningForm.USERNAME
				}),
			'first_name':
				forms.TextInput({
					'placeholder': 'Имя',
					'pattern': RUSSIAN_PATTERN,
					'title': WarningForm.FIRST_NAME
				}),
			'last_name':
				forms.TextInput({
					'placeholder': 'Фамилия',
					'pattern': RUSSIAN_PATTERN,
					'title': WarningForm.LAST_NAME
				}),
			'middle_name':
				forms.TextInput({
					'placeholder': 'Отчество',
					'pattern': RUSSIAN_PATTERN,
					'title': WarningForm.MIDDLE_NAME
				}),
			'group':
				forms.TextInput({'placeholder': 'Группа'}),
		}
		labels = {
			'comment': '',
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['password1'].widget = forms.PasswordInput(
			attrs={
				'placeholder': 'Пароль',
				'autocomplete': 'new-password'
			}
		)
		self.fields['password2'].widget = forms.PasswordInput(
			attrs={
				'placeholder': 'Подтверждение пароля',
				'autocomplete': 'new-password'
			}
		)

	def clean(self, *args, **kwargs) -> dict[str, str]:
		super().clean(*args, **kwargs)
		form_data: dict[str, str] = self.cleaned_data
		if not has_only_english_and_number_letters(form_data['username']):
			raise forms.ValidationError(WarningForm.USERNAME.value)

		if not has_only_russian_letters(form_data['first_name'].strip()):
			raise forms.ValidationError(WarningForm.FIRST_NAME.value)
		form_data['first_name'] = form_data['first_name'].strip().title()

		if not has_only_russian_letters(form_data['last_name'].strip()):
			raise forms.ValidationError(WarningForm.LAST_NAME.value)
		form_data['last_name'] = form_data['last_name'].strip().title()

		if not has_only_russian_letters(form_data['middle_name'].strip()):
			raise forms.ValidationError(WarningForm.MIDDLE_NAME.value)
		form_data['middle_name'] = form_data['middle_name'].strip().title()

		form_data['group'] = form_data['group'].upper()

		return form_data
