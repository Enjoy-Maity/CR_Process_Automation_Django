# Rendering Architecture

```mermaid
%% chunk:1/2
%%{init:{'theme':'base','themeVariables':{'background':'#060810','primaryColor':'#0c1a30','primaryTextColor':'#7dd3fc','primaryBorderColor':'#0e3a6e','edgeLabelBackground':'#0c1a30','lineColor':'#334155','secondaryColor':'#0f172a','clusterBkg':'#060c18','clusterBorder':'#1e3a5f','fontFamily':'JetBrains Mono','fontSize':'14'},'flowchart':{'nodeSpacing':25,'rankSpacing':8,'padding':4}}}%%
graph TD
  classDef ssr fill:#0d1a0d,stroke:#16a34a,color:#86efac
  classDef ctrl fill:#042f2e,stroke:#0d9488,color:#5eead4
  classDef csr fill:#2d1200,stroke:#c2410c,color:#fb923c
  classDef ssg fill:#1a0d1a,stroke:#7c3aed,color:#c4b5fd
  classDef isr fill:#1a1a0d,stroke:#ca8a04,color:#fde047
  classDef ppr fill:#0d1a2d,stroke:#2563eb,color:#93c5fd
  classDef unk fill:#1a1a1a,stroke:#6b7280,color:#9ca3af
  classDef pkg fill:#0c1018,stroke:#475569,color:#cbd5e1
  classDef ext fill:#2d1a06,stroke:#d97706,color:#fcd34d
  classDef muted fill:#0a0d14,stroke:#374151,color:#64748b,stroke-dasharray: 3 3
  classDef hdr fill:#06080f,stroke:#1e3a5f,color:#7dd3fc
  subgraph HDR_PKG ["📁 src/main/java/cr_process_automation.cr_process_automation"]
    direction TB
  leaf_urls["`📄 **urls**
─────────────
/admin`"]:::ctrl
  end
%%--CHUNK--%%
%% chunk:2/2
%%{init:{'theme':'base','themeVariables':{'background':'#060810','primaryColor':'#0c1a30','primaryTextColor':'#7dd3fc','primaryBorderColor':'#0e3a6e','edgeLabelBackground':'#0c1a30','lineColor':'#334155','secondaryColor':'#0f172a','clusterBkg':'#060c18','clusterBorder':'#1e3a5f','fontFamily':'JetBrains Mono','fontSize':'14'},'flowchart':{'nodeSpacing':25,'rankSpacing':8,'padding':4}}}%%
graph TD
  classDef ssr fill:#0d1a0d,stroke:#16a34a,color:#86efac
  classDef ctrl fill:#042f2e,stroke:#0d9488,color:#5eead4
  classDef csr fill:#2d1200,stroke:#c2410c,color:#fb923c
  classDef ssg fill:#1a0d1a,stroke:#7c3aed,color:#c4b5fd
  classDef isr fill:#1a1a0d,stroke:#ca8a04,color:#fde047
  classDef ppr fill:#0d1a2d,stroke:#2563eb,color:#93c5fd
  classDef unk fill:#1a1a1a,stroke:#6b7280,color:#9ca3af
  classDef pkg fill:#0c1018,stroke:#475569,color:#cbd5e1
  classDef ext fill:#2d1a06,stroke:#d97706,color:#fcd34d
  classDef muted fill:#0a0d14,stroke:#374151,color:#64748b,stroke-dasharray: 3 3
  classDef hdr fill:#06080f,stroke:#1e3a5f,color:#7dd3fc
  subgraph HDR_PKG ["📁 src/main/java/cr_process_automation.dashboard"]
    direction TB
  leaf_urls["`📄 **urls**
─────────────
/login
/logout
/home
/dashboard
/night-spoc
/region-crs
/cr\_history
/api/task/start/:task\_id
/api/task/dashboard-data
/download/task/:task\_id
/filter-region-crs
/region-crs/fetch-region-cr-details
/cr\_history/fetch-region-cr-details
/region-crs/save-region-cr-details
/fetch-cr-history
/download-cr-history
/playwright-auth-iframe
/playwright-password-iframe
/api/task/submit-otp/:task\_id
/api/task/submit-password/:task\_id
/cr\_wise\_status
/fetch-cr-wise-status
/fetch-user-options
/api/replica-sync-status/:sync\_id
/night-execution
/night-execution/fetch-crs
/night-execution/fetch-cr-status
/night-execution/start-task
/night-execution/status-result
/night-execution/submit-password
/night-execution/submit-otp
/night-execution/password-iframe
/night-execution/otp-iframe
/vendor-wise-analysis
/fetch-vendor-wise-analysis
/cr-success-rate-analysis
/fetch-cr-success-rate-analysis
/team-performance-analysis
/fetch-team-performance-analysis
/automation-cr-analysis
/fetch-automation-cr-analysis`"]:::ctrl
  end
```
