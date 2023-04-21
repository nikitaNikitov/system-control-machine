"""
Модуль для привязки url к методам обработки
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from .views import (
	accesses,
	generate_qr,
	index_page,
	login_user,
	logout_user,
	machines,
	manage,
	profile,
	profile_username,
	register_user,
)

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', index_page),
	path('logout/', logout_user, name='logout'),
	path('login/', login_user, name='login'),
	path('signup/', register_user),
	path('profile/', profile),
	path('profile/<username>', profile_username),
	path('manage', manage, name='manage'),
	path('machines', machines, name='machines'),
	path('qr/', generate_qr, name='generate_qr'),
	path('accesses', accesses),
	path('api/', include('api.urls')),
	path(
		'robots.txt',
		lambda x: HttpResponse("User-Agent: *\nDisallow:", content_type="text/plain"),
		name="robots_file"
	),
]
