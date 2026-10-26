from django.urls import path
from Administrator import views

app_name = 'Administrator'

urlpatterns = [
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    
    path('VerifyCompanies/', views.VerifyCompanies, name='VerifyCompanies'),
    path('ApproveCompanyAction/<int:cid>/<int:status>/', views.ApproveCompanyAction, name='ApproveCompanyAction'),
    
    path('VerifyStudents/', views.VerifyStudents, name='VerifyStudents'),
    path('ApproveStudentAction/<int:sid>/<int:status>/', views.ApproveStudentAction, name='ApproveStudentAction'),
    
    path('VerifyFaculties/', views.VerifyFaculties, name='VerifyFaculties'),
    path('AddFaculty/', views.AddFaculty, name='AddFaculty'),
    path('AssignFaculty/<int:sid>/', views.AssignFaculty, name='AssignFaculty'),
    path('AssignFacultyAction/<int:sid>/<int:fid>/', views.AssignFacultyAction, name='AssignFacultyAction'),
    
    # Master Data CRUD
    path('Department/', views.Department, name='Department'),
    path('edit_department/<int:did>/', views.edit_department, name='edit_department'),
    path('del_department/<int:did>/', views.del_department, name='del_department'),
    
    path('Programme/', views.Programme, name='Programme'),
    path('edit_programme/<int:pid>/', views.edit_programme, name='edit_programme'),
    path('del_programme/<int:did>/', views.del_programme, name='del_programme'),
    
    path('AcademicYear/', views.AcademicYear, name='AcademicYear'),
    path('del_academicyear/<int:yid>/', views.del_academicyear, name='del_academicyear'),
    path('Batch/', views.Batch, name='Batch'),
    path('del_batch/<int:bid>/', views.del_batch, name='del_batch'),

    # Activity Category Management
    path('ActivityCategory/', views.ActivityCategory, name='ActivityCategory'),
    path('edit_activitycategory/<int:cid>/', views.edit_activitycategory, name='edit_activitycategory'),
    path('toggle_activitycategory/<int:cid>/', views.toggle_activitycategory, name='toggle_activitycategory'),

    # Credit Requirement Configurator
    path('CreditRequirement/', views.CreditRequirement, name='CreditRequirement'),
    path('del_creditrequirement/<int:rid>/', views.del_creditrequirement, name='del_creditrequirement'),

    # Academic Activity Management
    path('AcademicActivity/', views.AcademicActivity, name='AcademicActivity'),
    path('edit_academicactivity/<int:aid>/', views.edit_academicactivity, name='edit_academicactivity'),
    path('update_activity_status/<int:aid>/<int:status>/', views.update_activity_status, name='update_activity_status'),
    path('ViewActivityRegistrations/<int:aid>/', views.ViewActivityRegistrations, name='ViewActivityRegistrations'),

    # Student Progress Monitoring
    path('StudentProgressMonitoring/', views.StudentProgressMonitoring, name='StudentProgressMonitoring'),
    path('CertificateMonitoring/', views.CertificateMonitoring, name='CertificateMonitoring'),
    path('InternshipMonitoring/', views.InternshipMonitoring, name='InternshipMonitoring'),

    # Notifications, Audit Logs, and Reports
    path('Notifications/', views.Notifications, name='Notifications'),
    path('AuditLogs/', views.AuditLogs, name='AuditLogs'),
    path('Reports/', views.Reports, name='Reports'),
]

