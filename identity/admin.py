from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Person, teacherCourses, VerificationEmail
from .models import Admin


# Register your models here

# class PersonInline(admin.StackedInline):
#     model = Person
#     can_delete = False
#     verbose_name_plural = 'person'
#
#
# class UserAdmin(BaseUserAdmin):
#     inlines = (PersonInline,)

class studentAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'username', 'user_icon', 'tags')
    verbose_name = "studentProfile"


admin.site.register(Person, studentAdmin)


class teacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'admin_name')


admin.site.register(Admin, teacherAdmin)

admin.site.register(teacherCourses)


class emailVerifyAdmin(admin.ModelAdmin):
    list_display = ('verification_code', 'email')


admin.site.register(VerificationEmail, emailVerifyAdmin)

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register()
