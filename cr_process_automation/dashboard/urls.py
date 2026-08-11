from django.urls import path
from . import views
from dashboard.Region_CRs import views as Region_views
from dashboard.CR_Wise_Status import views as CR_Wise_Status_views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("*logout/", views.logout_view, name="logout"),
    path("home/", views.cr_planning_view, name="cr_planning"),
    path('night-execution/', views.night_execution_view, name='night_execution'),
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
    
    
]
