"""
Модуль, связаный с функциями админки
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Machine, Perm, QRCode

admin.site.register(QRCode)
admin.site.register(Machine)
admin.site.register(Perm)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	"""
	Класс кастомного админа

	Создан для добавления дополнительных полей на странице управления пользователей в базе данных
	"""

	inlines = []
	model = CustomUser

	list_display = ['username', 'first_name', 'last_name', 'middle_name', 'group', 'is_staff']

	add_fieldsets = (
		*UserAdmin.add_fieldsets,
		(
			'Пользовательские поля', {
				'fields': ('first_name', 'last_name', 'middle_name', 'group', 'status', 'data')
			}
		),
	)

	fieldsets = ( # type: ignore # Невозможно адекватно указать тип данных
		*UserAdmin.fieldsets,
		('Пользовательские поля', {
		'fields': ('middle_name', 'group', 'status', 'data')
		}),
	)
