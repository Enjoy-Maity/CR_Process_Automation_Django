# Data Flow (Screen ↔ Data Source)

```mermaid
%%{init:{'theme':'base','themeVariables':{'background':'#060810','primaryColor':'#2a4055','primaryTextColor':'#f8fafc','primaryBorderColor':'#1e4060','lineColor':'#f59e0b','secondaryColor':'#0f172a','tertiaryColor':'#1a0a20','attributeBackgroundColorEven':'#ffffff','attributeBackgroundColorOdd':'#f1f5f9','textColor':'#1e293b','nodeBorder':'#1e4060','clusterBkg':'#0a0e1a','fontFamily':'JetBrains Mono','fontSize':'14'}}}%%
erDiagram
%% table:CoWModel path:cr_process_automation/dashboard/models.py
%% table:AutomationTask path:cr_process_automation/dashboard/models.py
%% table:TaskRun path:cr_process_automation/dashboard/models.py
%% table:TaskLog path:cr_process_automation/dashboard/models.py
%% table:cr_wise_status path:cr_process_automation/dashboard/models.py
%% table:FlagTable path:cr_process_automation/dashboard/models.py
  CoWModel {
    BooleanField is_active
    IntegerField version
    ForeignKey_self parent_reference FK
  }
  AutomationTask {
    PositiveIntegerField sequence_no
    CharField name
    BooleanField upload_required
    BooleanField download_required
    CharField current_status
    BooleanField active
    DateTimeField created_at
    DateTimeField updated_at
  }
  TaskRun {
    ForeignKey_AutomationTask task FK
    ForeignKey_AUTH_USER_MODEL triggered_by FK
    CharField status
    DateTimeField started_at
    DateTimeField completed_at
  }
  TaskLog {
    ForeignKey_TaskRun run FK
    CharField level
    TextField message
    DateTimeField created_at
  }
  cr_wise_status {
    IntegerField sno
    DateField execution_date
    CharField maintenance_window
    CharField cr_no
    CharField risk
    TextField activity_description
    CharField bpms_cr_yes_no
    CharField circle
    CharField region
    CharField technical_validator
    CharField CR_Hygiene_Checks
    CharField Install_Test_Plan_Downloads
    CharField MOP_Attachment
    CharField CR_Approvals
    CharField NIAM_Ticket
    BooleanField is_active
    IntegerField version
    ForeignKey_self parent_reference FK
  }
  FlagTable {
    CharField source_id
    BooleanField status
    IntegerField version
  }
  TaskRun }o--|| AutomationTask : "task"
  TaskLog }o--|| TaskRun : "run"
```
