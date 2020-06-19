from django.contrib import admin
from django.utils.html import format_html

from .models import History, Lab, Person


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('name','my_url_field',)
    readonly_fields = ["hash"]

    def my_url_field(self, obj):

        return format_html('<a href=" %s/admin/qrcode/%s%s">%s</a>' % ( "http://127.0.0.1:8000", obj.hash+"/",obj.name , obj.name))

    my_url_field.allow_tags = True
    my_url_field.short_description = 'QR generate'


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')
    search_fields = ('person__first_name','person__last_name', 'lab__name',)

    
admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(Person)
