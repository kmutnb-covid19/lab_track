from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import History, Lab, LabPending, Person


# Register your models here.


class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'action',)
    readonly_fields = ["hash"]
    empty_changelist_value = 'unknown'

    def get_queryset(self, request):
        queryset = super(LabAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            lab_list = []
            for lab_name in request.user.groups.all():
                lab_list.append(lab_name.name)
            return queryset.filter(name__in=lab_list)

    def action(self, obj):
        return format_html(
            '<a class="button" href="{}">View current user</a>&nbsp;&nbsp;&nbsp;&nbsp;'
            '<a class="button" href="{}" download>Download QR Code</a>',
            reverse('view_lab', args=[obj.hash]),
            reverse('generate_qr_code', args=[obj.hash]),
        )

    action.short_description = 'Actions'
    action.allow_tags = True


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'lab', 'checkin', 'checkout')
    search_fields = ('person__first_name', 'person__last_name', 'lab__name',)


admin.site.register(History, HistoryAdmin)
admin.site.register(Lab, LabAdmin)
admin.site.register(LabPending)
admin.site.register(Person)
