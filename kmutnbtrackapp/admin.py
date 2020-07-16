from django.contrib import admin
from django.utils.html import format_html

from .models import History, Lab, Person
from django.contrib.admin.views import main


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('names', 'view_lab', 'my_url_field',)
    readonly_fields = ["hash"]
    empty_changelist_value = 'unknown'

    def get_queryset(self, request):
        queryset = super(LabAdmin, self).get_queryset(request)
        self.request = request
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(name=self.request.user.groups.first())

    def names(self, obj):
        if self.request.user.is_superuser:
            return obj.name
        elif self.request.user.groups.filter(name=obj.name).exists():
            return obj.name


    def get_queryset(self, request):
        queryset = super(LabAdmin, self).get_queryset(request)
        self.request = request
        return queryset

    def names(self, obj):
        if self.request.user.is_superuser:
            return obj.name
        if not self.request.user.groups.filter(name=obj.name).exists():
            return ""
        return obj.name

    def my_url_field(self, obj):
        if self.request.user.is_superuser:
            return format_html('<button><a href="/admin/qrcode/%s/" download>%s</a></button>' % (obj.hash, obj.name))
        elif self.request.user.groups.filter(name=obj.name).exists():
            return format_html('<button><a href="/admin/qrcode/%s/" download>%s</a></button>' % (obj.hash, obj.name))

    my_url_field.allow_tags = True
    my_url_field.short_description = 'Download QR code'

    def view_lab(self, obj):
        if self.request.user.is_superuser:
            return format_html('<button><a href="/admin/clear/%s/">View %s</a></button>' % (obj.hash, obj.name))
        elif self.request.user.groups.filter(name=obj.name).exists():
            return format_html('<button><a href="/admin/clear/%s/">View %s</a></button>' % (obj.hash, obj.name))

    view_lab.allow_tags = True
    view_lab.short_description = 'View current user in lab'


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')
    search_fields = ('person__first_name', 'person__last_name', 'lab__name',)


admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(Person)
