from django.contrib import admin
from  .models import codes
# Register your models here.
class CodesAdmin(admin.ModelAdmin):
    list_display = ['code_id',
                    'code_content',
                    'compile_status',
                    'run_status_time',
                    'run_status_memory']
admin.site.register(codes, CodesAdmin)