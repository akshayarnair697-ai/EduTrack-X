from django.urls import path
from Company import views

app_name = 'Company'

urlpatterns = [
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('PostOpportunity/', views.PostOpportunity, name='PostOpportunity'),
    path('ViewOpportunities/', views.ViewOpportunities, name='ViewOpportunities'),
    path('EditOpportunity/<int:oid>/', views.EditOpportunity, name='EditOpportunity'),
    path('DelOpportunity/<int:oid>/', views.DelOpportunity, name='DelOpportunity'),
    path('InternshipApplications/', views.InternshipApplications, name='InternshipApplications'),
    path('UpdateApplicationStatus/<int:app_id>/<int:status>/', views.UpdateApplicationStatus, name='UpdateApplicationStatus'),
    path('MyProfile/', views.MyProfile, name='MyProfile'),
    path('EditProfile/', views.EditProfile, name='EditProfile'),
    path('ChangePassword/', views.ChangePassword, name='ChangePassword'),
    path('AddStudyMaterial/', views.AddStudyMaterial, name='AddStudyMaterial'),
    path('ViewStudyMaterials/', views.ViewStudyMaterials, name='ViewStudyMaterials'),
    path('DelStudyMaterial/<int:mid>/', views.DelStudyMaterial, name='DelStudyMaterial'),
    path('AssignTask/', views.AssignTask, name='AssignTask'),
    path('ViewCompanyTasks/', views.ViewCompanyTasks, name='ViewCompanyTasks'),
    path('DelTask/<int:tid>/', views.DelTask, name='DelTask'),
    path('ManageInterns/', views.ManageInterns, name='ManageInterns'),
    path('CompanyEvaluation/<int:iid>/', views.CompanyEvaluation, name='CompanyEvaluation'),
    path('ManageAttendance/', views.ManageAttendance, name='ManageAttendance'),
    path('InternAttendance/<int:iid>/', views.InternAttendance, name='InternAttendance'),
    path('UpdateAttendanceRecord/<int:aid>/', views.UpdateAttendanceRecord, name='UpdateAttendanceRecord'),
    path('Notifications/', views.Notifications, name='Notifications'),
]

