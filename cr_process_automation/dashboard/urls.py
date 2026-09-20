from django.urls import path
from . import views
from dashboard.Region_CRs import views as Region_views
from dashboard.CR_Wise_Status import views as CR_Wise_Status_views
# from dashboard.vendor_dashboard import views as VendorDashboard_views
# from dashboard.vendor_dashboard.views import vendor_dashboard_view, vendor_dashboard_data
from dashboard.Night_Execution import views as NightExecution_views


urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("*logout/", views.logout_view, name="logout"),
    path("home/", views.cr_planning_view, name="cr_planning"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # path('night-execution/', views.night_execution_view, name='night_execution'),
    path('night-spoc/', views.night_spoc_view, name='night_spoc'),
    path('region-crs/', Region_views.region_crs_view, name='region_crs'),
    path('cr_history/', Region_views.cr_history_view, name='cr_history'),
    # path('api/task/upload/<int:task_id>/', views.upload_task_file, name='upload_task_file'),
    path('api/task/start/<int:task_id>/', views.start_task, name='start_task'),
    path('api/task/dashboard-data/', views.task_dashboard_data, name='task_dashboard_data'),
    path('download/task/<int:task_id>/', views.download_task_output, name='download_task_output'),
    
    # path("import-master-cr/", views.import_master_cr_view, name="import-master-cr")
    # path('playwright-auth-iframe/', views.playwright_auth_iframe, name='playwright_auth_iframe'),
    path('filter-region-crs/', views.filter_region_crs, name="filter_region_crs"),
    path('region-crs/fetch-region-cr-details/', Region_views.fetch_region_cr_details, name='fetch_region_cr_details'),
    path('cr_history/fetch-region-cr-details/', Region_views.fetch_region_cr_details, name='fetch_region_cr_details'),
    path("region-crs/save-region-cr-details", Region_views.save_region_cr_details, name="save_region_cr_details"),
    path('fetch-cr-history/', Region_views.fetch_cr_history, name='fetch_cr_history'),
    path('download-cr-history/', Region_views.download_cr_history, name='download_cr_history'),
    
    path('playwright-auth-iframe/', views.playwright_auth_iframe, name='playwright_auth_iframe'),
    path("playwright-password-iframe/", views.playwright_password_iframe, name="playwright_password_iframe"),

    path("api/task/submit-otp/<int:task_id>/", views.submit_otp, name="submit_otp"),
    path("api/task/submit-password/<int:task_id>/", views.submit_password, name="submit_password"),  # NEW
    
    path('cr_wise_status/', CR_Wise_Status_views.cr_wise_status, name='cr_wise_status'),
    path('fetch-cr-wise-status/', CR_Wise_Status_views.fetch_cr_wise_status, name='fetch_cr_wise_status'),
    # CHANGED: new URL
    path("fetch-user-options/", views.fetch_user_options, name="fetch_user_options"),
    
    path('api/replica-sync-status/<str:sync_id>/', views.check_replica_sync_status, name='replica_sync_status'),


    #  path('dashboard/vendor-wise/', VendorDashboard_views.vendor_dashboard_view, name='vendor_dashboard'),
    # path('api/dashboard/vendor-wise-data/', VendorDashboard_views.vendor_dashboard_data, name='vendor_dashboard_data'),
    # path("vendor-dashboard/", vendor_dashboard_view, name="vendor_dashboard_view"),
    # path("api/dashboard/vendor-wise-data/", vendor_dashboard_data, name="vendor_dashboard_data"),

    path('night-execution/', NightExecution_views.night_execution, name='night_execution'),
    path('night-execution/fetch-crs/', NightExecution_views.fetch_night_execution_crs, name='fetch_night_execution_crs'),
    path('night-execution/fetch-cr-status/', NightExecution_views.fetch_night_cr_status, name='fetch_night_cr_status'),
    path('night-execution/start-task/', NightExecution_views.start_night_execution_task, name='start_night_execution_task'),

    # path('night-execution/start-status/', NightExecution_views.start_night_cr_status, name='start_night_cr_status'),
    path('night-execution/status-result/', NightExecution_views.night_cr_status_result, name='night_cr_status_result'),
    path('night-execution/submit-password/', NightExecution_views.submit_night_password, name='submit_night_password'),
    path('night-execution/submit-otp/', NightExecution_views.submit_night_otp, name='submit_night_otp'),
    path('night-execution/password-iframe/', NightExecution_views.night_password_iframe, name='night_password_iframe'),
    path('night-execution/otp-iframe/', NightExecution_views.night_otp_iframe, name='night_otp_iframe'),


    path("vendor-wise-analysis/", views.vendor_wise_analysis_view, name="vendor_wise_analysis"),
    path("fetch-vendor-wise-analysis/", views.fetch_vendor_wise_analysis, name="fetch_vendor_wise_analysis"),
    path("cr-success-rate-analysis/", views.cr_success_rate_analysis_view,name="cr_success_rate_analysis"),
    path("fetch-cr-success-rate-analysis/", views.fetch_cr_success_rate_analysis, name="fetch_cr_success_rate_analysis"),
    path("team-performance-analysis/", views.team_performance_analysis_view, name="team_performance_analysis"),
    path("fetch-team-performance-analysis/", views.fetch_team_performance_analysis, name="fetch_team_performance_analysis"),
    path("automation-cr-analysis/", views.automation_cr_analysis_view, name="automation_cr_analysis"),
    path("fetch-automation-cr-analysis/", views.fetch_automation_cr_analysis, name="fetch_automation_cr_analysis"),
]
