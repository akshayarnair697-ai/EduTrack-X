from django.urls import path
from Faculty import views

app_name = 'Faculty'

urlpatterns = [
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('AssignedStudents/', views.AssignedStudents, name='AssignedStudents'),
    path('MonitorStudent/<int:sid>/', views.MonitorStudent, name='MonitorStudent'),
    path('MyProfile/', views.MyProfile, name='MyProfile'),
    path('EditProfile/', views.EditProfile, name='EditProfile'),
    path('ChangePassword/', views.ChangePassword, name='ChangePassword'),

    # Activity Approvals
    path('ActivityApprovals/', views.ActivityApprovals, name='ActivityApprovals'),
    path('ApproveActivityAction/<int:rid>/<int:status>/', views.ApproveActivityAction, name='ApproveActivityAction'),

    # Certificate Verification
    path('CertificateVerifications/', views.CertificateVerifications, name='CertificateVerifications'),
    path('VerifyCertificateAction/<int:cid>/', views.VerifyCertificateAction, name='VerifyCertificateAction'),

    # Internship Monitoring & Progress
    path('InternshipMonitoring/', views.InternshipMonitoring, name='InternshipMonitoring'),
    path('StudentAttendance/<int:iid>/', views.StudentAttendance, name='StudentAttendance'),
    path('ReviewProgressReport/<int:pid>/', views.ReviewProgressReport, name='ReviewProgressReport'),
    path('EvaluateInternship/<int:iid>/', views.EvaluateInternship, name='EvaluateInternship'),

    # Credit Approvals, Notifications & Reports
    path('CreditApproval/', views.CreditApproval, name='CreditApproval'),
    path('Notifications/', views.Notifications, name='Notifications'),
    path('Reports/', views.Reports, name='Reports'),
]

