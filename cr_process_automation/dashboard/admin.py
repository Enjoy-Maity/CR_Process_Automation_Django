from django.contrib import admin
from .models import AutomationTask, TaskRun, TaskLog, MasterCRDatabase, CRWiseStatus, SelectedDateTable

from django.contrib.auth.admin import UserAdmin
from .models import UserManagement

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

@admin.register(UserManagement)
class UserManagementAdmin(UserAdmin):
    model = UserManagement
    list_display = ("username", "employee_name", "employee_signum", "role", "email", "last_login", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "employee_name", "employee_signum")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("User Management", {"fields": ("employee_name", "employee_signum", "role")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("User Management", {"fields": ("email", "employee_name", "employee_signum", "role")}),
    )	

@admin.register(CRWiseStatus)
class CRWiseStatusAdmin(admin.ModelAdmin):
    list_display = (
        "cr_no", "execution_date", "activity_description", "circle", "region", "technical_validator",
        "CR_Hygiene_Checks", "Install_Test_Plan_Downloads", "MOP_Attachment", "CR_Approvals", "NIAM_Ticket"
    )
    list_filter = (
        "region", "circle", "cr_no", "technical_validator", 
        "CR_Hygiene_Checks", "Install_Test_Plan_Downloads", "MOP_Attachment", "CR_Approvals", "NIAM_Ticket"
    )
    search_fields = (
        "region", "circle", "cr_no", "technical_validator"
    )
    ordering = ("-execution_date",)

@admin.register(SelectedDateTable)
class SelectedDateTableAdmin(admin.ModelAdmin):
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
