from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from datetime import date, datetime
from django.utils import timezone
from Guest.models import tbl_student, tbl_faculty, tbl_company
from Student.models import tbl_studentcredit, tbl_studentactivity, tbl_certificate
from Company.models import (
    tbl_opportunity, tbl_internship, tbl_studymaterial, tbl_task,
    tbl_internshipprogress, tbl_internshipreport, tbl_internshipattendance
)
from Administrator.models import tbl_activitycategory, tbl_academicactivity, tbl_creditrequirement, tbl_academicyear, tbl_notification
from Administrator.utils import create_notification, log_action, get_student_credit_summary

def Dashboard(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    summary = get_student_credit_summary(student.id)
    applications_count = tbl_internship.objects.filter(student=student).count()
    accepted_count = tbl_internship.objects.filter(student=student, internship_status__in=[2, 3, 4, 5, 6, 7]).count()
    active_tasks = tbl_task.objects.filter(student=student, task_status__in=[0, 1]).count()
    registered_activities = tbl_studentactivity.objects.filter(student=student).count()

    context = {
        'student': student,
        'summary': summary,
        'applications_count': applications_count,
        'accepted_count': accepted_count,
        'active_tasks': active_tasks,
        'registered_activities': registered_activities,
    }
    return render(request, 'Student/Dashboard.html', context)

def BrowseOpportunities(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    opportunities = tbl_opportunity.objects.all().order_by('-id')

    search = request.GET.get('q')
    if search:
        opportunities = opportunities.filter(opportunity_title__icontains=search)

    return render(request, 'Student/BrowseOpportunities.html', {'opportunities': opportunities})

def ViewCompanyDetails(request, cid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=cid)
    opportunities = tbl_opportunity.objects.filter(company=company)
    return render(request, 'Student/ViewCompanyDetails.html', {'company': company, 'opportunities': opportunities})

def ApplyOpportunity(request, oid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    opportunity = tbl_opportunity.objects.get(id=oid)
    
    existing = tbl_internship.objects.filter(student=student, opportunity=opportunity).first()

    if request.method == "POST":
        if not existing:
            internship_obj = tbl_internship.objects.create(
                opportunity=opportunity,
                company=opportunity.company,
                student=student,
                faculty=student.assigned_faculty,
                assigned_faculty=student.assigned_faculty,
                internship_status=0 # Applied
            )
            create_notification('company', opportunity.company.id, 'New Internship Application', f"Student {student.student_name} applied for '{opportunity.opportunity_title}'.")
            log_action(student.student_name, 'Student', 'Applied for Internship', 'Internship', internship_obj.id)
        return redirect('Student:MyApplications')

    return render(request, 'Student/ApplyOpportunity.html', {'opportunity': opportunity, 'existing': existing})

def MyApplications(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    applications = tbl_internship.objects.filter(student=student).order_by('-id')
    return render(request, 'Student/MyApplications.html', {'applications': applications})

def MyProfile(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    return render(request, 'Student/MyProfile.html', {'student': student})

def EditProfile(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    if request.method == "POST":
        student.student_name = request.POST.get("txt_name")
        student.student_email = request.POST.get("txt_email")
        student.student_contact = request.POST.get("txt_contact")
        student.student_address = request.POST.get("txt_address")
        if request.FILES.get("photo"):
            student.student_photo = request.FILES.get("photo")
        student.save()
        log_action(student.student_name, 'Student', 'Updated Profile', 'Profile')
        return redirect('Student:MyProfile')

    return render(request, 'Student/EditProfile.html', {'student': student})

def ChangePassword(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    msg = None
    if request.method == "POST":
        old_pass = request.POST.get("txt_old")
        new_pass = request.POST.get("txt_new")
        confirm_pass = request.POST.get("txt_confirm")

        if student.student_password == old_pass:
            if new_pass == confirm_pass:
                student.student_password = new_pass
                student.save()
                msg = "Password updated successfully!"
            else:
                msg = "New passwords do not match."
        else:
            msg = "Current password incorrect."

    return render(request, 'Student/ChangePassword.html', {'msg': msg})

def StudyMaterials(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    materials = tbl_studymaterial.objects.all().order_by('-id')
    return render(request, 'Student/StudyMaterials.html', {'materials': materials})

def MyTasks(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    tasks = tbl_task.objects.filter(student=student).order_by('-id')
    return render(request, 'Student/MyTasks.html', {'tasks': tasks})

def SubmitTask(request, tid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    task = tbl_task.objects.get(id=tid, student_id=request.session['sid'])

    if request.method == "POST":
        status = request.POST.get("sel_status")
        remark = request.POST.get("txt_remark")
        file_submission = request.FILES.get("file_submission")

        if status:
            task.task_status = int(status)
        if remark:
            task.submission_remark = remark
        if file_submission:
            task.submission_file = file_submission
        
        if int(status) == 2 and not task.completed_date:
            from datetime import date
            task.completed_date = date.today()

        task.save()
        create_notification('company', task.company.id, 'Task Submitted', f"Student {task.student.student_name} submitted task '{task.task_title}'.")
        log_action(task.student.student_name, 'Student', 'Submitted Task', 'Task Management', task.id)
        return redirect('Student:MyTasks')

    return render(request, 'Student/SubmitTask.html', {'task': task})

# ==================== NEW EDUTRACK-X STUDENT VIEWS ====================

# 1. Academic Activities
def AcademicActivities(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    categories = tbl_activitycategory.objects.filter(status=1)
    
    activities = tbl_academicactivity.objects.filter(activity_status__in=[0, 1, 2]).order_by('-id')

    cat_id = request.GET.get('cat')
    sem_val = request.GET.get('sem')
    search_q = request.GET.get('q')

    if cat_id:
        activities = activities.filter(category_id=cat_id)
    if sem_val:
        activities = activities.filter(semester=sem_val)
    if search_q:
        activities = activities.filter(activity_title__icontains=search_q)

    # Filter eligibility for student
    eligible_activities = []
    for act in activities:
        is_prog_eligible = (act.eligible_programme is None or act.eligible_programme == student.programme)
        is_batch_eligible = (act.eligible_batch is None or act.eligible_batch == student.batch)
        is_eligible = is_prog_eligible and is_batch_eligible
        
        reg_obj = tbl_studentactivity.objects.filter(student=student, activity=act).first()

        eligible_activities.append({
            'activity': act,
            'is_eligible': is_eligible,
            'registration': reg_obj
        })

    return render(request, 'Student/AcademicActivities.html', {
        'categories': categories,
        'eligible_activities': eligible_activities,
        'student': student
    })

def ActivityDetails(request, aid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    activity = tbl_academicactivity.objects.get(id=aid)

    is_prog_eligible = (activity.eligible_programme is None or activity.eligible_programme == student.programme)
    is_batch_eligible = (activity.eligible_batch is None or activity.eligible_batch == student.batch)
    is_eligible = is_prog_eligible and is_batch_eligible

    registration = tbl_studentactivity.objects.filter(student=student, activity=activity).first()
    registered_count = tbl_studentactivity.objects.filter(activity=activity).count()

    return render(request, 'Student/ActivityDetails.html', {
        'activity': activity,
        'is_eligible': is_eligible,
        'registration': registration,
        'registered_count': registered_count
    })

def RegisterActivity(request, aid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    activity = tbl_academicactivity.objects.get(id=aid)

    existing = tbl_studentactivity.objects.filter(student=student, activity=activity).first()
    if not existing:
        reg_obj = tbl_studentactivity.objects.create(
            student=student,
            activity=activity,
            status=0 # Registered
        )
        if student.assigned_faculty:
            create_notification('faculty', student.assigned_faculty.id, 'Activity Registration', f"Student {student.student_name} registered for '{activity.activity_title}'.")
        log_action(student.student_name, 'Student', 'Registered for Academic Activity', 'Academic Activity', reg_obj.id)

    return redirect('Student:MyActivities')

def MyActivities(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    registrations = tbl_studentactivity.objects.filter(student=student).select_related('activity', 'activity__category').order_by('-id')
    return render(request, 'Student/MyActivities.html', {'registrations': registrations})

def CancelActivityRegistration(request, rid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    reg = tbl_studentactivity.objects.filter(id=rid, student=student).first()
    if reg and reg.status in [0, 1]:
        from datetime import date
        if reg.activity.registration_deadline >= date.today():
            reg.delete()
            log_action(student.student_name, 'Student', 'Cancelled Activity Registration', 'Academic Activity')
    return redirect('Student:MyActivities')


# 2. Certificate Management
def UploadCertificate(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    categories = tbl_activitycategory.objects.filter(status=1)
    my_activities = tbl_studentactivity.objects.filter(student=student, status__in=[0, 1, 2, 4, 5])

    if request.method == "POST":
        title = request.POST.get("txt_title", "").strip()
        cat_id = request.POST.get("sel_category")
        activity_reg_id = request.POST.get("sel_activity")
        issuing_org = request.POST.get("txt_issuing_org", "").strip()
        cert_no = request.POST.get("txt_cert_no", "").strip()
        issue_date = request.POST.get("txt_issue_date")
        cert_file = request.FILES.get("file_certificate")
        remarks = request.POST.get("txt_remarks", "").strip()

        if title and cat_id and issue_date and cert_file:
            cat = tbl_activitycategory.objects.get(id=cat_id)
            act_reg = tbl_studentactivity.objects.get(id=activity_reg_id) if activity_reg_id else None

            cert_obj = tbl_certificate.objects.create(
                student=student,
                related_activity=act_reg,
                activity_category=cat,
                certificate_title=title,
                issuing_organization=issuing_org,
                certificate_number=cert_no,
                issue_date=issue_date,
                certificate_file=cert_file,
                additional_remarks=remarks,
                status=0 # Submitted
            )

            if act_reg:
                act_reg.status = 5 # Certificate Pending
                act_reg.save()

            if student.assigned_faculty:
                create_notification('faculty', student.assigned_faculty.id, 'New Certificate Submitted', f"Student {student.student_name} submitted certificate '{title}' for verification.")
            log_action(student.student_name, 'Student', 'Submitted Certificate', 'Certificate Management', cert_obj.id)
            return redirect('Student:MyCertificates')

    return render(request, 'Student/UploadCertificate.html', {
        'categories': categories,
        'my_activities': my_activities
    })

def MyCertificates(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    certificates = tbl_certificate.objects.filter(student=student).select_related('activity_category', 'faculty').order_by('-id')
    return render(request, 'Student/MyCertificates.html', {'certificates': certificates})


# 3. Internship Progress & Final Report
def UpdateInternshipJoining(request, iid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    internship = tbl_internship.objects.get(id=iid, student=student)

    if request.method == "POST":
        start_date = request.POST.get("txt_start_date")
        end_date = request.POST.get("txt_expected_end_date")
        mode = request.POST.get("sel_mode", "On-site")
        location = request.POST.get("txt_location", "").strip()

        if start_date:
            internship.start_date = start_date
            internship.expected_end_date = end_date
            internship.internship_mode = mode
            internship.internship_location = location
            internship.internship_status = 3 # Internship Started
            internship.save()

            if student.assigned_faculty:
                create_notification('faculty', student.assigned_faculty.id, 'Internship Started', f"Student {student.student_name} started internship at {internship.company.company_name}.")
            log_action(student.student_name, 'Student', 'Updated Internship Joining Info', 'Internship', internship.id)
            return redirect('Student:MyApplications')

    return render(request, 'Student/UpdateInternshipJoining.html', {'internship': internship})

def InternshipProgress(request, iid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    internship = tbl_internship.objects.get(id=iid, student=student)
    progress_reports = tbl_internshipprogress.objects.filter(internship=internship, student=student).order_by('-id')

    if request.method == "POST":
        work_done = request.POST.get("txt_work_completed", "").strip()
        skills = request.POST.get("txt_skills_learned", "").strip()
        challenges = request.POST.get("txt_challenges", "").strip()
        hours = request.POST.get("txt_hours", "0").strip()
        doc = request.FILES.get("file_doc")

        if work_done:
            prog_obj = tbl_internshipprogress.objects.create(
                internship=internship,
                student=student,
                work_completed=work_done,
                skills_learned=skills,
                challenges_faced=challenges,
                hours_completed=int(hours) if hours.isdigit() else 0,
                supporting_document=doc,
                progress_status=0 # Submitted
            )

            internship.internship_status = 4 # In Progress
            internship.save()

            if student.assigned_faculty:
                create_notification('faculty', student.assigned_faculty.id, 'Internship Progress Update', f"Student {student.student_name} submitted a progress report for internship.")
            log_action(student.student_name, 'Student', 'Submitted Internship Progress Report', 'Internship Progress', prog_obj.id)
            return redirect('Student:InternshipProgress', iid=iid)

    return render(request, 'Student/InternshipProgress.html', {'internship': internship, 'progress_reports': progress_reports})

def InternshipFinalReport(request, iid):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    internship = tbl_internship.objects.get(id=iid, student=student)
    final_report = tbl_internshipreport.objects.filter(internship=internship, student=student).first()

    if request.method == "POST":
        report_file = request.FILES.get("file_report")
        completion_cert = request.FILES.get("file_certificate")

        if report_file:
            if not final_report:
                final_report = tbl_internshipreport.objects.create(
                    internship=internship,
                    student=student,
                    report_file=report_file,
                    completion_certificate=completion_cert,
                    faculty_status=0 # Submitted
                )
            else:
                final_report.report_file = report_file
                if completion_cert:
                    final_report.completion_certificate = completion_cert
                final_report.faculty_status = 0
                final_report.save()

            internship.internship_status = 6 # Under Faculty Review
            internship.save()

            create_notification('company', internship.company.id, 'Internship Final Report Submitted', f"Student {student.student_name} submitted final internship report.")
            if student.assigned_faculty:
                create_notification('faculty', student.assigned_faculty.id, 'Internship Final Report Review', f"Student {student.student_name} submitted final report for review.")
            log_action(student.student_name, 'Student', 'Submitted Internship Final Report', 'Internship', final_report.id)
            return redirect('Student:MyApplications')

    return render(request, 'Student/InternshipFinalReport.html', {'internship': internship, 'final_report': final_report})


# 4. Credit Tracker, Academic Progress & Completion Checker
def CreditTracker(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    summary = get_student_credit_summary(student.id)

    return render(request, 'Student/CreditTracker.html', {'student': student, 'summary': summary})

def AcademicProgress(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    summary = get_student_credit_summary(student.id)

    activities = tbl_studentactivity.objects.filter(student=student).select_related('activity').order_by('-id')
    certificates = tbl_certificate.objects.filter(student=student).order_by('-id')
    internships = tbl_internship.objects.filter(student=student).order_by('-id')

    return render(request, 'Student/AcademicProgress.html', {
        'student': student,
        'summary': summary,
        'activities': activities,
        'certificates': certificates,
        'internships': internships
    })

def ProgrammeCompletionCheck(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    summary = get_student_credit_summary(student.id)

    return render(request, 'Student/ProgrammeCompletionCheck.html', {'student': student, 'summary': summary})


# 5. Notifications & Reports
def Notifications(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    notifications = tbl_notification.objects.filter(recipient_role='student', recipient_id__in=[student.id, 0]).order_by('-created_at')
    notifications.update(is_read=True)

    return render(request, 'Student/Notifications.html', {'notifications': notifications})

def Reports(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    summary = get_student_credit_summary(student.id)

    activities = tbl_studentactivity.objects.filter(student=student, status__in=[4, 6]).select_related('activity')
    certificates = tbl_certificate.objects.filter(student=student, status=1)
    internships = tbl_internship.objects.filter(student=student, internship_status=7)

    return render(request, 'Student/Reports.html', {
        'student': student,
        'summary': summary,
        'activities': activities,
        'certificates': certificates,
        'internships': internships
    })

def Attendance(request):
    if 'sid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=request.session['sid'])
    # Find student's active internship
    internship = tbl_internship.objects.filter(
        student=student, 
        internship_status__in=[1, 2, 3, 4, 5, 6, 7]
    ).order_by('-id').first()

    today = timezone.localdate()
    today_attendance = None
    if internship:
        today_attendance = tbl_internshipattendance.objects.filter(
            internship=internship, 
            attendance_date=today
        ).first()

    if request.method == "POST" and internship:
        action = request.POST.get("action")
        now_time = timezone.localtime().time()

        if action == "check_in":
            if not today_attendance:
                today_attendance = tbl_internshipattendance.objects.create(
                    internship=internship,
                    student=student,
                    attendance_date=today,
                    check_in_time=now_time,
                    attendance_status=1,
                    verification_status=0 # Pending company review
                )
            elif not today_attendance.check_in_time:
                today_attendance.check_in_time = now_time
                today_attendance.attendance_status = 1
                today_attendance.save()
            return redirect('Student:Attendance')

        elif action == "check_out":
            if today_attendance:
                today_attendance.check_out_time = now_time
                hours_input = request.POST.get("hours_worked")
                if hours_input:
                    try:
                        today_attendance.hours_worked = round(float(hours_input), 2)
                    except ValueError:
                        pass
                elif today_attendance.check_in_time:
                    dt_in = datetime.combine(today, today_attendance.check_in_time)
                    dt_out = datetime.combine(today, now_time)
                    diff = (dt_out - dt_in).total_seconds() / 3600.0
                    today_attendance.hours_worked = max(round(diff, 2), 0.5)

                task_summary = request.POST.get("daily_tasks_summary", "").strip()
                if task_summary:
                    today_attendance.daily_tasks_summary = task_summary

                today_attendance.save()
            return redirect('Student:Attendance')

    # Metrics calculation
    attendances = []
    total_days = 0
    present_days = 0
    total_hours = 0.0
    attendance_rate = 0.0

    if internship:
        attendances = tbl_internshipattendance.objects.filter(internship=internship).order_by('-attendance_date')
        total_days = attendances.count()
        present_days = attendances.filter(attendance_status=1).count()
        total_hours = sum(float(a.hours_worked) for a in attendances)
        if total_days > 0:
            attendance_rate = round((present_days / total_days) * 100, 1)

    context = {
        'student': student,
        'internship': internship,
        'today': today,
        'today_attendance': today_attendance,
        'attendances': attendances,
        'total_days': total_days,
        'present_days': present_days,
        'total_hours': round(total_hours, 2),
        'attendance_rate': attendance_rate,
    }
    return render(request, 'Student/Attendance.html', context)

