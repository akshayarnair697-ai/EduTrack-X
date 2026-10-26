from django.db import models
from Administrator.models import tbl_department, tbl_programme, tbl_batch

class tbl_faculty(models.Model):
    faculty_name = models.CharField(max_length=100)
    faculty_email = models.CharField(max_length=100)
    faculty_contact = models.CharField(max_length=20)
    faculty_address = models.CharField(max_length=200)
    faculty_photo = models.FileField(upload_to='FacultyDocs/', null=True, blank=True)
    faculty_password = models.CharField(max_length=100)
    faculty_status = models.IntegerField(default=0) # 0: Pending, 1: Active, 2: Rejected
    faculty_date = models.DateField(auto_now_add=True)
    department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)

    def __str__(self):
        return self.faculty_name

class tbl_student(models.Model):
    student_regno = models.CharField(max_length=50, null=True, unique=True)
    student_name = models.CharField(max_length=100)
    student_gender = models.CharField(max_length=20)
    student_dob = models.DateField()
    student_email = models.CharField(max_length=100)
    student_contact = models.CharField(max_length=20)
    student_address = models.CharField(max_length=200)
    student_photo = models.FileField(upload_to='StudentDocs/', null=True, blank=True)
    student_password = models.CharField(max_length=100)
    student_status = models.IntegerField(default=0) # 0: Pending, 1: Active, 2: Rejected
    student_date = models.DateField(auto_now_add=True)
    programme = models.ForeignKey(tbl_programme, on_delete=models.CASCADE)
    batch = models.ForeignKey(tbl_batch, on_delete=models.CASCADE, null=True, blank=True)
    assigned_faculty = models.ForeignKey(tbl_faculty, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.student_name

class tbl_company(models.Model):
    company_name = models.CharField(max_length=100)
    company_email = models.CharField(max_length=100)
    company_contact = models.CharField(max_length=20)
    company_address = models.CharField(max_length=200)
    company_website = models.CharField(max_length=200, null=True, blank=True)
    company_industry = models.CharField(max_length=100, null=True, blank=True)
    company_description = models.CharField(max_length=500, null=True, blank=True)
    company_logo = models.FileField(upload_to='CompanyLogos/', null=True, blank=True)
    company_proof = models.FileField(upload_to='CompanyDocs/', null=True, blank=True)
    company_password = models.CharField(max_length=100)
    company_status = models.IntegerField(default=0) # 0: Pending, 1: Active, 2: Rejected
    company_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.company_name

