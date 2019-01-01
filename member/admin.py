from django.contrib import admin

from .models import Member, University, Major, Professor, Student, CreditLog

# Register your models here.
admin.site.register(Member)
admin.site.register(University)
admin.site.register(Major)
admin.site.register(Professor)
admin.site.register(Student)
admin.site.register(CreditLog)
