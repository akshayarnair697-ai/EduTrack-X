from django.db import models
from Guest.models import tbl_company, tbl_student, tbl_faculty

class tbl_opportunity(models.Model):
    company = models.ForeignKey(tbl_company, on_delete=models.CASCADE)
    opportunity_title = models.CharField(max_length=100, null=True)
    opportunity_description = models.CharField(max_length=500, null=True)
    skills_required = models.CharField(max_length=200, null=True)
    duration = models.CharField(max_length=50, null=True)
    stipend = models.CharField(max_length=50, default='Unpaid')
    last_date = models.DateField(null=True)
    posted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.opportunity_title} - {self.company.company_name}"

class tbl_internship(models.Model):
    opportunity = models.ForeignKey(tbl_opportunity, on_delete=models.CASCADE)
    company = models.ForeignKey(tbl_company, on_delete=models.CASCADE)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(tbl_faculty, on_delete=models.SET_NULL, null=True, blank=True)
    applied_date = models.DateField(auto_now_add=True)
    # Statuses: 0: Applied, 1: Under Review, 2: Selected, 3: Internship Started, 4: In Progress, 5: Report Pending, 6: Under Faculty Review, 7: Completed, 8: Rejected or Cancelled
    internship_status = models.IntegerField(default=0)
    evaluation_marks = models.IntegerField(null=True, blank=True)
    evaluation_remark = models.CharField(max_length=500, null=True, blank=True)
    credits_awarded = models.IntegerField(default=0)
    
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    internship_mode = models.CharField(max_length=50, default='On-site') # Remote, On-site, Hybrid
    internship_location = models.CharField(max_length=200, null=True, blank=True)
    assigned_faculty = models.ForeignKey(tbl_faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_internships')
    internship_credit = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.student.student_name} - {self.opportunity.opportunity_title}"

class tbl_studymaterial(models.Model):
    company = models.ForeignKey(tbl_company, on_delete=models.CASCADE)
    material_title = models.CharField(max_length=150)
    material_description = models.TextField(blank=True, null=True)
    material_file = models.FileField(upload_to='study_materials/')
    posted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_title} - {self.company.company_name}"

class tbl_task(models.Model):
    company = models.ForeignKey(tbl_company, on_delete=models.CASCADE)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    internship = models.ForeignKey(tbl_internship, on_delete=models.SET_NULL, null=True, blank=True)
    task_title = models.CharField(max_length=150)
    task_description = models.TextField()
    task_deadline = models.DateField(null=True, blank=True)
    task_file = models.FileField(upload_to='task_files/', null=True, blank=True)
    task_status = models.IntegerField(default=0) # 0: Pending, 1: In Progress, 2: Completed
    submission_file = models.FileField(upload_to='task_submissions/', null=True, blank=True)
    submission_remark = models.TextField(null=True, blank=True)
    assigned_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_title} -> {self.student.student_name}"

class tbl_internshipprogress(models.Model):
    internship = models.ForeignKey(tbl_internship, on_delete=models.CASCADE)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    reporting_date = models.DateField(auto_now_add=True)
    work_completed = models.TextField()
    skills_learned = models.TextField(null=True, blank=True)
    challenges_faced = models.TextField(null=True, blank=True)
    hours_completed = models.IntegerField(default=0)
    supporting_document = models.FileField(upload_to='internship_progress/', null=True, blank=True)
    progress_status = models.IntegerField(default=0) # 0: Submitted, 1: Reviewed
    faculty_remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Progress Report: {self.student.student_name} ({self.reporting_date})"

class tbl_internshipreport(models.Model):
    internship = models.ForeignKey(tbl_internship, on_delete=models.CASCADE)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='internship_reports/')
    completion_certificate = models.FileField(upload_to='internship_certs/', null=True, blank=True)
    submission_date = models.DateField(auto_now_add=True)
    faculty_status = models.IntegerField(default=0) # 0: Submitted, 1: Under Review, 2: Approved, 3: Rejected
    faculty_remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Final Report: {self.student.student_name}"

class tbl_companyevaluation(models.Model):
    internship = models.ForeignKey(tbl_internship, on_delete=models.CASCADE)
    technical_skills = models.IntegerField(default=5) # Rating 1-10
    communication = models.IntegerField(default=5)
    attendance = models.IntegerField(default=5)
    work_quality = models.IntegerField(default=5)
    teamwork = models.IntegerField(default=5)
    discipline = models.IntegerField(default=5)
    overall_performance = models.IntegerField(default=5)
    remarks = models.TextField(null=True, blank=True)
    confirmed_completion = models.BooleanField(default=False)
    evaluation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation: {self.internship.student.student_name}"

class tbl_internshipattendance(models.Model):
    internship = models.ForeignKey(tbl_internship, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) # e.g. 8.00
    # Status: 1: Present, 0: Absent, 2: Half Day, 3: On Leave, 4: Work From Home / Remote
    attendance_status = models.IntegerField(default=1)
    # Verification: 0: Pending, 1: Approved by Company, 2: Flagged / Adjusted
    verification_status = models.IntegerField(default=1)
    daily_tasks_summary = models.TextField(null=True, blank=True)
    company_remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('internship', 'attendance_date')
        ordering = ['-attendance_date', '-created_at']

    def __str__(self):
        return f"{self.student.student_name} - {self.attendance_date} ({self.hours_worked} hrs)"

