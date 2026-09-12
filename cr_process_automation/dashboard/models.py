from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, UniqueConstraint
from django.db import transaction



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
    cr_no = models.CharField(max_length=50,blank=False)
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

    # def save(self, *args, **kwargs):
    #     # CoW Save Override: Turn updates into insertions of a new active row
    #     if self.pk is not None:
    #         old_instance = MasterCRDatabase.objects.get(pk=self.pk)
    #         MasterCRDatabase.objects.filter(pk=self.pk).update(is_active=False)
    #         self.parent_reference_id = old_instance.pk
    #         self.version = old_instance.version + 1
    #         self.pk = None 
    #         self.is_active = True
    #     super().save(*args, **kwargs)


    def save(self, *args, skip_cow=False,  **kwargs):
        if skip_cow:
            super().save(*args, **kwargs)
            return
        
        if self.pk is not None:
            # with transaction.atomic():
            #     old_instance = (MasterCRDatabase.objects
            #                     .select_for_update()
            #                     .get(pk=self.pk))
            #     MasterCRDatabase.objects.filter(pk=self.pk).update(is_active=False)
            #     self.parent_reference_id = old_instance.pk
            #     self.version = old_instance.version + 1
            #     self.pk = None
            #     self.is_active = True
            #     super().save(*args, **kwargs)
            kwargs.pop("force_insert", None)
            kwargs.pop("update_fields", None)
            old_instance = MasterCRDatabase.objects.get(pk=self.pk)
            MasterCRDatabase.objects.filter(pk=self.pk).update(is_active=False)
            self.parent_reference_id = old_instance.pk
            self.version = old_instance.version + 1
            self.pk = None
            self.is_active = True
        super().save(*args, **kwargs)
        # else:
        #     super().save(*args, **kwargs)

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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ADMIN)
    
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
    cr_no = models.CharField(max_length=50, blank=False)
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
        db_table = "selected_date_table"
        constraints = [
            UniqueConstraint(
                fields=['cr_no'], 
                condition=Q(is_active=True), 
                name='unique_active_selected_table_cr_no'
            )
        ]

    def __str__(self):
        return self.cr_no

    # def save(self, *args, **kwargs):
    #     """
    #     Custom save method that implements Copy-on-Write (CoW) architecture
    #     and syncs changes to both SelectedDateTable and MasterCRDatabase.
    #     """
    #     # Flag to track if this is an update (not a new creation)
    #     is_update = self.pk is not None
        
    #     if is_update:
    #         # Step 1: Get the old instance before modification
    #         old_instance = SelectedDateTable.objects.get(pk=self.pk)
            
    #         # Step 2: Mark old version as inactive in SelectedDateTable
    #         SelectedDateTable.objects.filter(pk=self.pk).update(is_active=False)
            
    #         # Step 3: Prepare new version for SelectedDateTable
    #         self.parent_reference_id = old_instance.pk
    #         self.version = old_instance.version + 1
    #         self.pk = None  # Force insert as new row
    #         self.is_active = True
        
    #     # Step 4: Save to SelectedDateTable
    #     super().save(*args, **kwargs)
        
    #     # Step 5: Sync to MasterCRDatabase
    #     self._sync_to_master_cr_database(is_update)


    # def save(self, *args, **kwargs):
    #     with transaction.atomic():
    #         is_update = self.pk is not None
    #         if is_update:
    #             old_instance = (SelectedDateTable.objects
    #                             .select_for_update()
    #                             .get(pk=self.pk))
    #             SelectedDateTable.objects.filter(pk=self.pk).update(is_active=False)
    #             self.parent_reference_id = old_instance.pk
    #             self.version = old_instance.version + 1
    #             self.pk = None
    #             self.is_active = True
    #         super().save(*args, **kwargs)
    #         self._sync_to_master_cr_database(is_update)


    def save(self, *args, skip_cow=False, **kwargs):
        if skip_cow:
            super().save(*args, **kwargs)
            return
        # is_update = self.pk is not None
        # if is_update:
        using = self._state.db or kwargs.get("using")
        old_instance = None
        if self.pk is not None:
            qs = SelectedDateTable.objects
            if using:
                qs = qs.using(using)
            old_instance = qs.filter(pk=self.pk).first()   # None-safe, no exception

        if old_instance is not None:
            # old_instance = SelectedDateTable.objects.get(pk=self.pk)
            SelectedDateTable.objects.filter(pk=self.pk).update(is_active=False)
            self.parent_reference_id = old_instance.pk
            self.version = old_instance.version + 1
            self.pk = None
            self.is_active = True

        else:
            # No existing row for this pk -> plain insert as a new active v1.
            # Clear any stale pk so the DB assigns a fresh one.
            self.pk = None
            if not self.version:
                self.version = 1
            self.is_active = True

        super().save(*args, **kwargs)
        if not skip_cow:  # only sync on the CoW path
            self._sync_to_master_cr_database(old_instance is not None)


    # def _sync_to_master_cr_database(self, is_update):
    #     if not self.cr_no:
    #         raise ValueError("cr_no is required to sync to MasterCRDatabase")
    #     fields = dict(
    #         sno=self.sno, ms_project=self.ms_project, execution_date=self.execution_date,
    #         maintenance_window=self.maintenance_window, cr_no=self.cr_no, priority=self.priority,
    #         risk=self.risk, region=self.region, circle=self.circle, node_details=self.node_details,
    #         node_count=self.node_count, activity_description=self.activity_description,
    #         bpms_cr_yes_no=self.bpms_cr_yes_no, planning_status=self.planning_status,
    #         activity_executor=self.activity_executor, auditor_name=self.auditor_name,
    #         activity_status=self.activity_status, reason_for_rollback_cancel=self.reason_for_rollback_cancel,
    #         technical_validator=self.technical_validator, service_affecting=self.service_affecting,
    #         impact=self.impact, test_cases=self.test_cases, kpi_name=self.kpi_name,
    #         kpi_spoc_night=self.kpi_spoc_night, kpi_spoc_morning=self.kpi_spoc_morning,
    #         inter_domain_activity=self.inter_domain_activity,
    #         inter_domain_kpi_required=self.inter_domain_kpi_required,
    #         inter_domain_measuring_kpis=self.inter_domain_measuring_kpis,
    #         activity_type=self.activity_type, vendor=self.vendor, protocol=self.protocol,
    #         execution_type=self.execution_type, cli_availability=self.cli_availability,
    #         team=self.team, scheduled_start_date=self.scheduled_start_date,
    #         scheduled_end_date=self.scheduled_end_date, niam_ticket_required=self.niam_ticket_required,
    #         niam_node_type=self.niam_node_type, additional_info=self.additional_info,
    #     )

    #     with transaction.atomic():
    #         master_cr = (MasterCRDatabase.objects
    #                     .select_for_update()
    #                     .filter(cr_no=self.cr_no, is_active=True)
    #                     .first())

    #         if master_cr is None:
    #             # No active master: first insert for this cr_no
    #             MasterCRDatabase.objects.create(is_active=True, version=1, **fields)
    #             return

    #         # Active master exists. Apply new field values and let
    #         # MasterCRDatabase.save() perform the CoW versioning atomically.
    #         for key, value in fields.items():
    #             setattr(master_cr, key, value)
    #         master_cr.save()  # pk is set -> triggers CoW flip+insert inside this txn

    def _sync_to_master_cr_database(self, is_update):
        if not self.cr_no:
            raise ValueError("cr_no is required to sync to MasterCRDatabase")

        fields = dict(
            sno=self.sno, ms_project=self.ms_project, execution_date=self.execution_date,
            maintenance_window=self.maintenance_window, cr_no=self.cr_no, priority=self.priority,
            risk=self.risk, region=self.region, circle=self.circle, node_details=self.node_details,
            node_count=self.node_count, activity_description=self.activity_description,
            bpms_cr_yes_no=self.bpms_cr_yes_no, planning_status=self.planning_status,
            activity_executor=self.activity_executor, auditor_name=self.auditor_name,
            activity_status=self.activity_status, reason_for_rollback_cancel=self.reason_for_rollback_cancel,
            technical_validator=self.technical_validator, service_affecting=self.service_affecting,
            impact=self.impact, test_cases=self.test_cases, kpi_name=self.kpi_name,
            kpi_spoc_night=self.kpi_spoc_night, kpi_spoc_morning=self.kpi_spoc_morning,
            inter_domain_activity=self.inter_domain_activity,
            inter_domain_kpi_required=self.inter_domain_kpi_required,
            inter_domain_measuring_kpis=self.inter_domain_measuring_kpis,
            activity_type=self.activity_type, vendor=self.vendor, protocol=self.protocol,
            execution_type=self.execution_type, cli_availability=self.cli_availability,
            team=self.team, scheduled_start_date=self.scheduled_start_date,
            scheduled_end_date=self.scheduled_end_date, niam_ticket_required=self.niam_ticket_required,
            niam_node_type=self.niam_node_type, additional_info=self.additional_info,
        )

        # NOTE: No new atomic() here. This method must run inside the caller's
        # transaction (SelectedDateTable.save already opens transaction.atomic()).
        # Nesting a second atomic created savepoints that could partially roll
        # back and leave master/replica drift (0 or 2 active rows per cr_no).

        # master_cr = (
        #     MasterCRDatabase.objects
        #     .filter(cr_no=self.cr_no, is_active=True)
        #     .first()
        # )

        # if master_cr is None:
        #     # No active master yet: first insert for this cr_no.
        #     MasterCRDatabase.objects.create(is_active=True, version=1, **fields)
        #     return

        # # Active master exists. Overlay the new field values on the fetched row,
        # # then let MasterCRDatabase.save() perform the CoW flip+insert.
        # # Because save() nulls the pk and inserts a new active row, we must NOT
        # # pass update_fields/force_insert here.
        # for key, value in fields.items():
        #     setattr(master_cr, key, value)

        # master_cr.save()  # pk is set -> triggers CoW versioning in the same txn
        # Runs inside the caller's transaction (SelectedDateTable.save).
        active = list(
            MasterCRDatabase.objects.filter(cr_no=self.cr_no, is_active=True)
        )

        if not active:
            # No active master: first insert. skip_cow avoids re-entering CoW.
            MasterCRDatabase(is_active=True, version=1, **fields).save(skip_cow=True)
            return

        # Deactivate ALL active rows for this cr_no FIRST (defends against
        # accidental duplicates), then insert the new active version.
        old = active[0]
        MasterCRDatabase.objects.filter(cr_no=self.cr_no, is_active=True).update(is_active=False)

        MasterCRDatabase(
            is_active=True,
            version=old.version + 1,
            parent_reference_id=old.pk,
            **fields,
        ).save(skip_cow=True)  # plain insert; old rows already deactivated

