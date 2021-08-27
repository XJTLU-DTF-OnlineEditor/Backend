from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Person


# Register your models here.

class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name = 'person'


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


admin.site.register(Person)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
