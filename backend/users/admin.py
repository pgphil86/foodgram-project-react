from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')


admin.site.register(Follow)
