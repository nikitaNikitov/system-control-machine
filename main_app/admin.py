"""
Модуль, связаный с функциями админки
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
# admin.site.register(CustomUser)
# class CustomUserInline(admin.StackedInline):
#     model = CustomUser
#     can_delete = False
#     verbose_name_plural = 'Custom!'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Класс кастомного админа

    Создан для добавления дополнительных полей на странице управления пользователей в базе данных
    """
    inlines = []
    model = CustomUser

    list_display = ['username', 'first_name',
                    'last_name', 'middle_name', 'group', 'is_staff']

    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        (
            'Пользовательские поля',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'middle_name',
                    'group',
                    'status'
                )
            }
        )
    )

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Пользовательские поля',
            {
                'fields': (
                    'middle_name',
                    'group',
                    'status'
                )
            }
        )
    )

# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
