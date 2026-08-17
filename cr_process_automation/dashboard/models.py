from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, UniqueConstraint


class AutomationTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Successful', 'Successful'),
        ('Unsuccessful', 'Unsuccessful'),
    ]

    sequence_no = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    upload_required = models.BooleanField(default=False)
    download_required = models.BooleanField(default=False)
    current_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sequence_no']

    def __str__(self):
        return f"{self.sequence_no}. {self.name}"


class TaskRun(models.Model):
    RUN_STATUS_CHOICES = [
        ('Queued', 'Queued'),
        ('Running', 'Running'),
        ('Successful', 'Successful'),
        ('Unsuccessful', 'Unsuccessful'),
    ]

    task = models.ForeignKey(AutomationTask, on_delete=models.CASCADE, related_name='runs')
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=RUN_STATUS_CHOICES, default='Queued')
    uploaded_template = models.FileField(upload_to='task_templates/', null=True, blank=True)
    output_file = models.FileField(upload_to='task_outputs/', null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Run {self.id} - {self.task.name}"


class TaskLog(models.Model):
    run = models.ForeignKey(TaskRun, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, default='INFO')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.level}: {self.message[:60]}"

class MasterCRDatabase(models.Model):
    sno = models.IntegerField(null=True, blank=True)
    ms_project = models.CharField(max_length=100, null=True, blank=True)
    execution_date = models.DateField(null=True, blank=True)
    maintenance_window = models.CharField(max_length=50, null=True, blank=True)
    cr_no = models.CharField(max_length=50,)
    priority = models.CharField(max_length=50, null=True, blank=True)
    risk = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    circle = models.CharField(max_length=50, null=True, blank=True)
    node_details = models.TextField(null=True, blank=True)
    node_count = models.IntegerField(null=True, blank=True)
    activity_description = models.TextField(null=True, blank=True)
    bpms_cr_yes_no = models.CharField(max_length=10, null=True, blank=True)
    planning_status = models.CharField(max_length=50, null=True, blank=True)
    activity_executor = models.CharField(max_length=100, null=True, blank=True)
    auditor_name = models.CharField(max_length=100, null=True, blank=True)
    activity_status = models.CharField(max_length=100, null=True, blank=True)
    reason_for_rollback_cancel = models.TextField(null=True, blank=True)
    technical_validator = models.CharField(max_length=100, null=True, blank=True)
    service_affecting = models.CharField(max_length=10, null=True, blank=True)
    impact = models.TextField(null=True, blank=True)
    test_cases = models.TextField(null=True, blank=True)
    kpi_name = models.TextField(null=True, blank=True)
    kpi_spoc_night = models.CharField(max_length=100, null=True, blank=True)
    kpi_spoc_morning = models.CharField(max_length=100, null=True, blank=True)
    inter_domain_activity = models.CharField(max_length=10, null=True, blank=True)
    inter_domain_kpi_required = models.CharField(max_length=10, null=True, blank=True)
    inter_domain_measuring_kpis = models.TextField(null=True, blank=True)
    activity_type = models.CharField(max_length=200, null=True, blank=True)
    vendor = models.CharField(max_length=50, null=True, blank=True)
    protocol = models.CharField(max_length=100, null=True, blank=True)
    execution_type = models.CharField(max_length=50, null=True, blank=True)
    cli_availability = models.CharField(max_length=10, null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    scheduled_start_date = models.DateTimeField(null=True, blank=True)
    scheduled_end_date = models.DateTimeField(null=True, blank=True)
    niam_ticket_required = models.CharField(max_length=10, null=True, blank=True)
    niam_node_type = models.CharField(max_length=100, null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)

    # --- Copy-on-Write (CoW) Architecture Fields ---
    is_active = models.BooleanField(default=True, help_text="Indicates the current active version")
    version = models.IntegerField(default=1, help_text="Version number of this record")
    parent_reference = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='historical_versions',
        help_text="Links to the previous version of this record"
    )

    class Meta:
        db_table = "master_cr_database"
        # Enforce that only ONE active record can exist per cr_no (historical rows ignored)
        constraints = [
            UniqueConstraint(
                fields=['cr_no'], 
                condition=Q(is_active=True), 
                name='unique_active_master_cr_no'
            )
        ]

    def save(self, *args, **kwargs):
        # CoW Save Override: Turn updates into insertions of a new active row
        if self.pk is not None:
            old_instance = MasterCRDatabase.objects.get(pk=self.pk)
            MasterCRDatabase.objects.filter(pk=self.pk).update(is_active=False)
            self.parent_reference_id = old_instance.pk
            self.version = old_instance.version + 1
            self.pk = None 
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cr_no} (v{self.version})"

class UserManagement(AbstractUser):
    ROLE_ADMIN = "Admin"
    ROLE_VALIDATOR = "Validator"
    ROLE_NIGHT_SPOC = "Night-SPOC"
    ROLE_EXECUTOR = "Executor"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_VALIDATOR, "Validator"),
        (ROLE_NIGHT_SPOC, "Night-SPOC"),
        (ROLE_EXECUTOR, "Executor"),
    ]

    email = models.EmailField("user mail id", unique=True)
    employee_name = models.CharField(max_length=150, null=True, blank=True)
    employee_signum = models.CharField(max_length=100, null=True, blank=True, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EXECUTOR)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

# class CRWiseStatus(models.Model):
#     sno = models.IntegerField(null=True, blank=True)
#     execution_date = models.DateField(null=True, blank=True)
#     maintenance_window = models.CharField(max_length=50, null=True, blank=True)
#     cr_no = models.CharField(max_length=50, unique=True)
#     risk = models.CharField(max_length=100, null=True, blank=True)
#     activity_description = models.TextField(null=True, blank=True)
#     bpms_cr_yes_no = models.CharField(max_length=10, null=True, blank=True)
#     circle = models.CharField(max_length=50, null=True, blank=True)
#     region = models.CharField(max_length=50, null=True, blank=True)
#     technical_validator = models.CharField(max_length=100, null=True, blank=True)
#     CR_Hygiene_Checks = models.CharField(max_length=100, null=True, blank=True)
#     Install_Test_Plan_Downloads = models.CharField(max_length=100, null=True, blank=True)
#     MOP_Attachment = models.CharField(max_length=100, null=True, blank=True)
#     CR_Approvals = models.CharField(max_length=100, null=True, blank=True)
#     NIAM_Ticket = models.CharField(max_length=100, null=True, blank=True)

#     class Meta:
#             db_table = "cr_wise_status"
    
#     def __str__(self):
#         return self.cr_no


class CRWiseStatus(models.Model):
    sno = models.IntegerField(null=True, blank=True)
    execution_date = models.DateField(null=True, blank=True)
    maintenance_window = models.CharField(max_length=50, null=True, blank=True)
    
    # Critical: Unique constraint prevents duplicate CRs at DB level
    cr_no = models.CharField(max_length=50,) 
    
    risk = models.CharField(max_length=100, null=True, blank=True)
    activity_description = models.TextField(null=True, blank=True)
    bpms_cr_yes_no = models.CharField(max_length=10, null=True, blank=True)
    circle = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    technical_validator = models.CharField(max_length=100, null=True, blank=True)
    
    # Status Flags
    CR_Hygiene_Checks = models.CharField(max_length=100, null=True, blank=True)
    Install_Test_Plan_Downloads = models.CharField(max_length=100, null=True, blank=True)
    MOP_Attachment = models.CharField(max_length=100, null=True, blank=True)
    CR_Approvals = models.CharField(max_length=100, null=True, blank=True)
    NIAM_Ticket = models.CharField(max_length=100, null=True, blank=True)

    # --- Copy-on-Write (CoW) Architecture Fields ---
    is_active = models.BooleanField(default=True, help_text="Indicates the current active version")
    version = models.IntegerField(default=1, help_text="Version number of this record")
    parent_reference = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='historical_versions',
        help_text="Links to the previous version of this record"
    )

    class Meta:
        db_table = "cr_wise_status"
        # Enforce that only ONE active status record can exist per cr_no
        constraints = [
            UniqueConstraint(
                fields=['cr_no'], 
                condition=Q(is_active=True), 
                name='unique_active_cr_wise_status_no'
            )
        ]

    def save(self, *args, **kwargs):
        # CoW Save Override
        if self.pk is not None:
            old_instance = CRWiseStatus.objects.get(pk=self.pk)
            CRWiseStatus.objects.filter(pk=self.pk).update(is_active=False)
            self.parent_reference_id = old_instance.pk
            self.version = old_instance.version + 1
            self.pk = None 
            self.is_active = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cr_no} (v{self.version})"


class FlagTable(models.Model):
    source_id = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=False)
    version = models.IntegerField(default=0) # Optimistic locking helper


class SelectedDateTable(models.Model):
    sno = models.IntegerField(null=True, blank=True)
    ms_project = models.CharField(max_length=100, null=True, blank=True)
    execution_date = models.DateField(null=True, blank=True)
    maintenance_window = models.CharField(max_length=50, null=True, blank=True)
    cr_no = models.CharField(max_length=50, unique=True)
    priority = models.CharField(max_length=50, null=True, blank=True)
    risk = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    circle = models.CharField(max_length=50, null=True, blank=True)
    node_details = models.TextField(null=True, blank=True)
    node_count = models.IntegerField(null=True, blank=True)
    activity_description = models.TextField(null=True, blank=True)
    bpms_cr_yes_no = models.CharField(max_length=10, null=True, blank=True)
    planning_status = models.CharField(max_length=50, null=True, blank=True)
    activity_executor = models.CharField(max_length=100, null=True, blank=True)
    auditor_name = models.CharField(max_length=100, null=True, blank=True)
    activity_status = models.CharField(max_length=100, null=True, blank=True)
    reason_for_rollback_cancel = models.TextField(null=True, blank=True)
    technical_validator = models.CharField(max_length=100, null=True, blank=True)
    service_affecting = models.CharField(max_length=10, null=True, blank=True)
    impact = models.TextField(null=True, blank=True)
    test_cases = models.TextField(null=True, blank=True)
    kpi_name = models.TextField(null=True, blank=True)
    kpi_spoc_night = models.CharField(max_length=100, null=True, blank=True)
    kpi_spoc_morning = models.CharField(max_length=100, null=True, blank=True)
    inter_domain_activity = models.CharField(max_length=10, null=True, blank=True)
    inter_domain_kpi_required = models.CharField(max_length=10, null=True, blank=True)
    inter_domain_measuring_kpis = models.TextField(null=True, blank=True)
    activity_type = models.CharField(max_length=200, null=True, blank=True)
    vendor = models.CharField(max_length=50, null=True, blank=True)
    protocol = models.CharField(max_length=100, null=True, blank=True)
    execution_type = models.CharField(max_length=50, null=True, blank=True)
    cli_availability = models.CharField(max_length=10, null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    scheduled_start_date = models.DateTimeField(null=True, blank=True)
    scheduled_end_date = models.DateTimeField(null=True, blank=True)
    niam_ticket_required = models.CharField(max_length=10, null=True, blank=True)
    niam_node_type = models.CharField(max_length=100, null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "selected_date_table"

    def __str__(self):
        return self.cr_no
    