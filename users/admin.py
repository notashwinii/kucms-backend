# File: kucms/users/admin.py

from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'is_student', 'is_faculty', 'get_user_type')
    search_fields = ('email',)
    readonly_fields = ('date_joined',)

    def get_email(self, obj):
        return obj.email

    get_email.short_description = 'Email'

    def get_user_type(self, obj):
        return obj.get_user_type

    get_user_type.short_description = 'User Type'

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('date_joined',)
