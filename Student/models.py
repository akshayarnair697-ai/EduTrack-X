from django.db import models
from Guest.models import tbl_student, tbl_faculty
from Administrator.models import tbl_activitycategory, tbl_academicactivity, tbl_academicyear

class tbl_studentcredit(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    credit_category = models.ForeignKey(tbl_activitycategory, on_delete=models.SET_NULL, null=True, blank=True)
    credit_type = models.CharField(max_length=100, null=True, blank=True) # Fallback / descriptive label
    credit_value = models.IntegerField(default=0)
    source_type = models.CharField(max_length=100, default='Other Approved Activity') # Academic Activity, Certificate, Internship, Project, Workshop, Seminar, Add-on Course, Other Approved Activity
    source_reference = models.CharField(max_length=100, null=True, blank=True)
    academic_year = models.ForeignKey(tbl_academicyear, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    approval_status = models.IntegerField(default=1) # 0: Pending, 1: Approved, 2: Rejected
    approved_by = models.ForeignKey(tbl_faculty, on_delete=models.SET_NULL, null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    credit_remark = models.CharField(max_length=200, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    credit_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.credit_type or self.source_type} ({self.credit_value} Credits)"

class tbl_studentactivity(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    activity = models.ForeignKey(tbl_academicactivity, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)
    status = models.IntegerField(default=0) # 0: Registered, 1: Pending Approval, 2: Approved, 3: Rejected, 4: Completed, 5: Certificate Pending, 6: Credit Awarded
    faculty_remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.activity.activity_title}"

class tbl_certificate(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    related_activity = models.ForeignKey(tbl_studentactivity, on_delete=models.SET_NULL, null=True, blank=True)
    activity_category = models.ForeignKey(tbl_activitycategory, on_delete=models.CASCADE)
    certificate_title = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    certificate_number = models.CharField(max_length=100, null=True, blank=True)
    issue_date = models.DateField()
    certificate_file = models.FileField(upload_to='certificates/')
    submission_date = models.DateField(auto_now_add=True)
    additional_remarks = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=0) # 0: Submitted, 1: Approved, 2: Rejected, 3: Resubmission Required
    faculty = models.ForeignKey(tbl_faculty, on_delete=models.SET_NULL, null=True, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    faculty_remarks = models.TextField(null=True, blank=True)
    confirmed_credit = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.student_name} - {self.certificate_title}"

