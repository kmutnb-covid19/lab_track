from django.contrib import admin
from .models import History, Lab, StudentID
# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display= ('lab_name',)

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'lab_name', 'checkin', 'checkout')

admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
