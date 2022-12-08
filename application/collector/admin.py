from django.contrib import admin
from django.template.defaultfilters import truncatechars

from .models import (
    AndroidOs,
    Changelists,
    ModelInfo,
    QueryHistory,
    TasksInformation,
    CarrierInformation,
)


class AndroidOsAdmin(admin.ModelAdmin):
    list_display = ["os_version", "os_code"]


class ChangelistsAdmin(admin.ModelAdmin):
    list_display = [
        "cl_number",
        "get_tasks",
        "model",
        "branch",
        "os",
        "cl_source",
        "cl_type",
        "relevance",
        "is_smr",
        "get_carrier_codes",
        "comment",
    ]

    def get_tasks(self, obj):
        tasks_str = ", ".join([t.task_code for t in obj.task_list.all()])
        return truncatechars(tasks_str, 40)

    def get_carrier_codes(self, obj):
        tasks_str = ", ".join([t.carrier_code for t in obj.carrier_info.all()])
        return truncatechars(tasks_str, 40)


class TasksInformationAdmin(admin.ModelAdmin):
    list_display = ["task_code", "model"]


class ModelInfoAdmin(admin.ModelAdmin):
    list_display = ["short_model_name", "model_name", "project", "os"]


class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ["model", "os", "date"]


class CarrierInformationAdmin(admin.ModelAdmin):
    list_display = ["carrier_code"]


admin.site.register(AndroidOs, AndroidOsAdmin)
admin.site.register(Changelists, ChangelistsAdmin)
admin.site.register(ModelInfo, ModelInfoAdmin)
admin.site.register(TasksInformation, TasksInformationAdmin)
admin.site.register(QueryHistory, QueryHistoryAdmin)
admin.site.register(CarrierInformation, CarrierInformationAdmin)
