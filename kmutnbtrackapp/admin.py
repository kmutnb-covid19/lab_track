from django.contrib import admin
from .models import History, Lab, Person


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('name',)


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')


admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(Person)
