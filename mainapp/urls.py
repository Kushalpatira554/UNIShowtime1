from django.urls import path
from django.shortcuts import redirect
from . import views
from .views import approve_event, reject_event

def home_redirect(request):
    return redirect('dashboard')

urlpatterns = [
    # Filter endpoints
    path('filter-events/', views.filter_events, name='filter_events'),
    path('filter-users/', views.filter_users, name='filter_users'),
    path('approve-event/<int:event_id>/', approve_event, name='approve_event'),
    path('reject-event/<int:event_id>/', reject_event, name='reject_event'),
    path('', home_redirect),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('user/<int:user_id>/', views.admin_user_details, name='admin_user_details'),
    path('create-event/', views.create_event, name='create_event'),
    path('suggest-event/', views.suggest_event, name='suggest_event'),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('ticket/<int:ticket_id>/qr/', views.qr_view, name='qr_view'),
    path('ticket/<int:ticket_id>/download/', views.qr_download, name='qr_download'),
    path('event/<int:event_id>/', views.event_details, name='event_details'),
    path('event/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('event/<int:event_id>/admin/', views.admin_event_details, name='admin_event_details'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:event_id>/memories/', views.event_memories, name='event_memories'),
    path('event/<int:event_id>/add-memory/', views.add_event_memory, name='add_event_memory'),
    path('department/<int:department_id>/', views.department_details, name='department_details'),
    path('department/create/', views.create_department, name='create_department'),
    path('department/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('department/<int:department_id>/delete/', views.delete_department, name='delete_department'),
    path('user/<int:user_id>/details/', views.user_details, name='user_details'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/create/', views.create_user, name='create_user'),
    path('system/settings/', views.system_settings, name='system_settings'),
    path('system/logs/', views.system_logs, name='system_logs'),
    path('system/backup/', views.system_backup, name='system_backup'),
    path('system/backup/create/', views.create_backup, name='create_backup'),
    path('system/backup/restore/<int:backup_id>/', views.restore_backup, name='restore_backup'),
    path('system/backup/upload_and_restore/', views.upload_and_restore_backup, name='upload_and_restore_backup'),
    path('system/backup/download/<int:backup_id>/', views.download_backup, name='download_backup'),
    path('system/backup/delete/<int:backup_id>/', views.delete_backup, name='delete_backup'),
    path('system/logs/clear/', views.clear_logs, name='clear_logs'),
    path('system/logs/export/', views.export_logs, name='export_logs'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('contact/', views.contact_view, name='contact'),
]
