from django.contrib import admin
from .models import Person, VerificationEmail
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
from .student_action_models import History, Collect


class studentAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'username', 'user_icon', 'tags')
    verbose_name = "studentProfile"


admin.site.register(Person, studentAdmin)


class teacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'admin_name')


admin.site.register(Admin, teacherAdmin)


class emailVerifyAdmin(admin.ModelAdmin):
    list_display = ('verification_code', 'email')


admin.site.register(VerificationEmail, emailVerifyAdmin)


class HistoryAdmin(admin.ModelAdmin):
    list_display = ("person", "topic", "last_practice_time")
    filter_vertical = ("finished_courses",)  # 多对多显示

    
admin.site.register(History, HistoryAdmin)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ("person", "topic", "collect_time")


admin.site.register(Collect, CollectionAdmin)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register()
