from django.db import models

class tbl_adminregistration(models.Model):
    adminregistration_name = models.CharField(max_length=100)
    adminregistration_contact = models.CharField(max_length=100)
    adminregistration_email = models.CharField(max_length=100)
    adminregistration_password = models.CharField(max_length=100)

    def __str__(self):
        return self.adminregistration_name

class tbl_department(models.Model):
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class tbl_programme(models.Model):
    programme_name = models.CharField(max_length=100)
    programme_duration = models.IntegerField()
    programme_totalcredit = models.IntegerField()
    department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)

    def __str__(self):
        return self.programme_name

class tbl_batch(models.Model):
    batch_name = models.CharField(max_length=100)

    def __str__(self):
        return self.batch_name

class tbl_academicyear(models.Model):
    academicyear_name = models.CharField(max_length=100)

    def __str__(self):
        return self.academicyear_name

class tbl_activitycategory(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    default_credit = models.IntegerField(default=0)
    status = models.IntegerField(default=1) # 1: Active, 0: Inactive

    def __str__(self):
        return self.category_name

class tbl_creditrequirement(models.Model):
    programme = models.ForeignKey(tbl_programme, on_delete=models.CASCADE)
    activity_category = models.ForeignKey(tbl_activitycategory, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(tbl_academicyear, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    required_credit = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.programme.programme_name} - {self.activity_category.category_name}: {self.required_credit} Credits"

class tbl_academicactivity(models.Model):
    activity_title = models.CharField(max_length=200)
    category = models.ForeignKey(tbl_activitycategory, on_delete=models.CASCADE)
    description = models.TextField()
    conducting_org = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=50)
    academic_year = models.ForeignKey(tbl_academicyear, on_delete=models.CASCADE)
    semester = models.IntegerField(default=1)
    eligible_programme = models.ForeignKey(tbl_programme, on_delete=models.SET_NULL, null=True, blank=True)
    eligible_batch = models.ForeignKey(tbl_batch, on_delete=models.SET_NULL, null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    registration_deadline = models.DateField()
    credit_value = models.IntegerField(default=0)
    required_proof = models.CharField(max_length=200, default='Certificate')
    activity_status = models.IntegerField(default=1) # 0: Upcoming, 1: Open for Registration, 2: Ongoing, 3: Completed, 4: Closed

    def __str__(self):
        return self.activity_title

class tbl_notification(models.Model):
    recipient_role = models.CharField(max_length=20) # student, faculty, company, admin
    recipient_id = models.IntegerField(default=0) # 0 for all/admin or specific user ID
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_url = models.CharField(max_length=200, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.recipient_role}] {self.title}"

class tbl_auditlog(models.Model):
    user_name = models.CharField(max_length=100)
    user_role = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    related_module = models.CharField(max_length=100)
    related_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user_name} ({self.action})"

