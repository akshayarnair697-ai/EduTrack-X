from django.urls import path
from Student import views

app_name = 'Student'

urlpatterns = [
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('BrowseOpportunities/', views.BrowseOpportunities, name='BrowseOpportunities'),
    path('ViewCompanyDetails/<int:cid>/', views.ViewCompanyDetails, name='ViewCompanyDetails'),
    path('ApplyOpportunity/<int:oid>/', views.ApplyOpportunity, name='ApplyOpportunity'),
    path('MyApplications/', views.MyApplications, name='MyApplications'),
    path('MyProfile/', views.MyProfile, name='MyProfile'),
    path('EditProfile/', views.EditProfile, name='EditProfile'),
    path('ChangePassword/', views.ChangePassword, name='ChangePassword'),
    path('StudyMaterials/', views.StudyMaterials, name='StudyMaterials'),
    path('MyTasks/', views.MyTasks, name='MyTasks'),
    path('SubmitTask/<int:tid>/', views.SubmitTask, name='SubmitTask'),

    # Academic Activities
    path('AcademicActivities/', views.AcademicActivities, name='AcademicActivities'),
    path('ActivityDetails/<int:aid>/', views.ActivityDetails, name='ActivityDetails'),
    path('RegisterActivity/<int:aid>/', views.RegisterActivity, name='RegisterActivity'),
    path('MyActivities/', views.MyActivities, name='MyActivities'),
    path('CancelActivityRegistration/<int:rid>/', views.CancelActivityRegistration, name='CancelActivityRegistration'),

    # Certificate Management
    path('UploadCertificate/', views.UploadCertificate, name='UploadCertificate'),
    path('MyCertificates/', views.MyCertificates, name='MyCertificates'),

    # Internship Progress & Final Report
    path('UpdateInternshipJoining/<int:iid>/', views.UpdateInternshipJoining, name='UpdateInternshipJoining'),
    path('InternshipProgress/<int:iid>/', views.InternshipProgress, name='InternshipProgress'),
    path('InternshipFinalReport/<int:iid>/', views.InternshipFinalReport, name='InternshipFinalReport'),

    # Credit Tracker & Academic Progress
    path('CreditTracker/', views.CreditTracker, name='CreditTracker'),
    path('AcademicProgress/', views.AcademicProgress, name='AcademicProgress'),
    path('ProgrammeCompletionCheck/', views.ProgrammeCompletionCheck, name='ProgrammeCompletionCheck'),

    # Attendance & Daily Logs
    path('Attendance/', views.Attendance, name='Attendance'),

    # Notifications & Reports
    path('Notifications/', views.Notifications, name='Notifications'),
    path('Reports/', views.Reports, name='Reports'),
]

