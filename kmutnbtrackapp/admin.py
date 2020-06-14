from django.contrib import admin
from .models import History, Lab, Person


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ["hash"]


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')
    search_fields = ('person__first_name','person__last_name', 'lab__name',)

    
admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(Person)
