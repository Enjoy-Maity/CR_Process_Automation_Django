from django.contrib import admin
from .models import AutomationTask, TaskRun, TaskLog
from .models import MasterCRDatabase 


@admin.register(AutomationTask)
class AutomationTaskAdmin(admin.ModelAdmin):
    list_display = ('sequence_no', 'name', 'current_status', 'upload_required', 'download_required', 'active', 'updated_at')
    list_filter = ('current_status', 'upload_required', 'download_required', 'active')
    search_fields = ('name',)
    ordering = ('sequence_no',)


class TaskLogInline(admin.TabularInline):
    model = TaskLog
    extra = 0
    readonly_fields = ('level', 'message', 'created_at')
    can_delete = False


@admin.register(TaskRun)
class TaskRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'triggered_by', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('task__name', 'triggered_by__username')
    autocomplete_fields = ('task', 'triggered_by')
    inlines = [TaskLogInline]


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'level', 'short_message', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('message', 'run__task__name')

    def short_message(self, obj):
        return obj.message[:80]
    short_message.short_description = 'Message'

@admin.register(MasterCRDatabase)
class MasterCRDatabaseAdmin(admin.ModelAdmin):
    list_display = (
        "cr_no", "execution_date", "region", "circle", "priority",
        "planning_status", "activity_status", "vendor", "team"
    )
    list_filter = (
        "region", "circle", "priority", "planning_status", "activity_status",
        "vendor", "team", "service_affecting", "inter_domain_activity"
    )
    search_fields = (
        "cr_no", "activity_description", "node_details", "region", "circle",
        "vendor", "team", "activity_executor", "auditor_name"
    )
    ordering = ("-execution_date",)