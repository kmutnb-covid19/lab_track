from django.contrib import admin
from django.utils.html import format_html

from .models import History, Lab, Person


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_lab', 'my_url_field',)
    readonly_fields = ["hash"]

    def my_url_field(self, obj):
        return format_html('<button><a href="/admin/qrcode/%s/" download>%s</a></button>' % (obj.hash, obj.name))

    my_url_field.allow_tags = True
    my_url_field.short_description = 'Download QR code'

    def view_lab(self, obj):
        return format_html('<button><a href="/admin/clear/%s/">View %s</a></button>' % (obj.hash, obj.name))

    view_lab.allow_tags = True
    view_lab.short_description = 'View current user in lab'


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')
    search_fields = ('person__first_name', 'person__last_name', 'lab__name',)


admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(Person)
