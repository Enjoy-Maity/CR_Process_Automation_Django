from django.urls import path
from . import views
urlpatterns = [
    path('', views.cr_planning_view, name='cr_planning'),
    path('night-execution/', views.night_execution_view, name='night_execution'),
    path('night-spoc/', views.night_spoc_view, name='night_spoc'),
    path('region-crs/', views.region_crs_view, name='region_crs'),
    # path('api/task/upload/<int:task_id>/', views.upload_task_file, name='upload_task_file'),
    path('api/task/start/<int:task_id>/', views.start_task, name='start_task'),
    path('api/task/dashboard-data/', views.task_dashboard_data, name='task_dashboard_data'),
    path('download/task/<int:task_id>/', views.download_task_output, name='download_task_output'),
    
    # path("import-master-cr/", views.import_master_cr_view, name="import-master-cr")
    path('playwright-auth-iframe/', views.playwright_auth_iframe, name='playwright_auth_iframe'),
    path("playwright-password-iframe/", views.playwright_password_iframe, name="playwright_password_iframe"),

    path("api/task/submit-otp/<int:task_id>/", views.submit_otp, name="submit_otp"),
    path("api/task/submit-password/<int:task_id>/", views.submit_password, name="submit_password"),  # NEW
]
