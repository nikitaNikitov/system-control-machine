"""
Модуль для привязки API url к методам
"""
from django.urls import path

from .views import (
	accesses,
	add_machine,
	delete_machine,
	get_qr,
	get_user_from_code,
	give_permission,
	manage,
	manage_machine,
	regenerate_machine_token,
	revoke_permission,
	show_machines,
)

urlpatterns = [
	path('getUser', get_user_from_code),
	path('qr', get_qr),
	path('users', manage),
	path('users/<machine>', manage_machine),
	path('givePermission', give_permission),
	path('revokePermission', revoke_permission),
	path('addMachine', add_machine),
	path('deleteMachine', delete_machine),
	# path('revokePermission', revoke_permission),
	path('machines', show_machines),
	path('regenerateAccessToken', regenerate_machine_token),
	path('accesses', accesses),
]
