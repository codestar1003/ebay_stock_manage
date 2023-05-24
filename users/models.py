from django.db import models
from django.contrib.auth.models import AbstractUser

from dry_rest_permissions.generics import authenticated_users


class User(AbstractUser):
    email = models.EmailField(max_length=250)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    
    def has_read_permission(request):
        return True

    def has_register_permission(request):
        return True

    def has_login_permission(request):
        return True
    
    @authenticated_users
    def has_write_permission(request):
        return True
