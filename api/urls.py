"""
Модуль для привязки API url к методам
"""
from django.urls import path

from .views import (
	get_qr,
	get_user_from_code,
	get_user_from_code_machine,
	give_permission,
	manage,
	manage_machine,
)

urlpatterns = [
	path('getUser', get_user_from_code),
	path('getUser/<machine>', get_user_from_code_machine),
	path('qr', get_qr),
	path('users', manage),
	path('users/<machine>', manage_machine),
	path('givePermission', give_permission),
	# path('revokePermission', revoke_permission),
]
