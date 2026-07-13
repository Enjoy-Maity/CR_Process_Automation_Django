# myapp/management/commands/import_master_cr.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.models import MasterCRDatabase


class Command(BaseCommand):
    help = "Import Master CR database from Excel"

    def handle(self, *args, **options):
        excel_path = os.path.join(settings.BASE_DIR, "cr_process_automation", "PS-Core daily planning sheet.xlsx")

        if not os.path.exists(excel_path):
            self.stderr.write(f"File not found: {excel_path}")
            return

        df = pd.read_excel(excel_path, sheet_name="Planning_Sheet")

        rename_map = {
            "S.No.": "sno",
            "MS/Project": "ms_project",
            "Execution Date": "execution_date",
            "Maintainence Window": "maintenance_window",
            "CR No": "cr_no",
            "Priority": "priority",
            "Risk": "risk",
            "Region": "region",
            "Circle": "circle",
            "Node Details": "node_details",
            "Node Count": "node_count",
            "Activity Description": "activity_description",
            "BPMS CR (Yes/No)": "bpms_cr_yes_no",
            "Planning Status": "planning_status",
            "Activity Executor": "activity_executor",
            "Auditor Name": "auditor_name",
            "Activity Status": "activity_status",
            "Reason For Rollback/Cancel": "reason_for_rollback_cancel",
            "Technical Validator": "technical_validator",
            "Service Affecting": "service_affecting",
            "Impact": "impact",
            "Test Cases": "test_cases",
            "KPI Name": "kpi_name",
            "KPI SPOC (Night)": "kpi_spoc_night",
            "KPI SPOC (Morning)": "kpi_spoc_morning",
            "Inter-Domain Activity": "inter_domain_activity",
            "Inter-Domain KPI Required": "inter_domain_kpi_required",
            "Inter-Domain Measuring KPIs": "inter_domain_measuring_kpis",
            "Activity Type": "activity_type",
            "Vendor": "vendor",
            "Protocol": "protocol",
            "Execution Type": "execution_type",
            "CLI Availability": "cli_availability",
            "Team": "team",
            "Scheduled Start Date+": "scheduled_start_date",
            "Scheduled End Date+": "scheduled_end_date",
            "NIAM Ticket Required (Yes/No)": "niam_ticket_required",
            "NIAM Node Type": "niam_node_type",
            "Additional Info": "additional_info",
        }

        df = df.rename(columns=rename_map)

        for col in ["execution_date", "scheduled_start_date", "scheduled_end_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        df = df.where(pd.notnull(df), None)

        created = 0
        for row in df.to_dict(orient="records"):
            if not row.get("cr_no"):
                continue

            obj, was_created = MasterCRDatabase.objects.update_or_create(
                cr_no=row["cr_no"],
                defaults=row,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created} records successfully."))