from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from Guest.models import tbl_student, tbl_faculty
from Student.models import tbl_studentcredit, tbl_studentactivity, tbl_certificate
from Company.models import tbl_internship, tbl_internshipprogress, tbl_internshipreport, tbl_companyevaluation, tbl_task, tbl_internshipattendance
from Administrator.models import tbl_activitycategory, tbl_academicactivity, tbl_creditrequirement, tbl_notification
from Administrator.utils import create_notification, log_action, get_student_credit_summary

def Dashboard(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    assigned_students = tbl_student.objects.filter(assigned_faculty=faculty)
    assigned_count = assigned_students.count()

    # Pending items for faculty dashboard counter badges
    pending_certificates = tbl_certificate.objects.filter(student__in=assigned_students, status=0).count()
    pending_activities = tbl_studentactivity.objects.filter(student__in=assigned_students, status=1).count()
    pending_reports = tbl_internshipreport.objects.filter(student__in=assigned_students, faculty_status=0).count()
    active_interns = tbl_internship.objects.filter(student__in=assigned_students, internship_status__in=[3, 4, 5, 6]).count()

    context = {
        'faculty': faculty,
        'assigned_count': assigned_count,
        'assigned_students': assigned_students,
        'pending_certificates': pending_certificates,
        'pending_activities': pending_activities,
        'pending_reports': pending_reports,
        'active_interns': active_interns,
    }
    return render(request, 'Faculty/Dashboard.html', context)

def AssignedStudents(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    students = tbl_student.objects.filter(assigned_faculty=faculty)
    
    student_data = []
    for s in students:
        summary = get_student_credit_summary(s.id)
        student_data.append({
            'student': s,
            'summary': summary
        })

    return render(request, 'Faculty/AssignedStudents.html', {'student_data': student_data})

def MonitorStudent(request, sid):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    student = tbl_student.objects.get(id=sid, assigned_faculty=faculty)
    
    # Ownership check: faculty can only monitor assigned student or department student
    summary = get_student_credit_summary(student.id)
    activities = tbl_studentactivity.objects.filter(student=student).order_by('-id')
    certificates = tbl_certificate.objects.filter(student=student).order_by('-id')
    internships = tbl_internship.objects.filter(student=student).order_by('-id')

    context = {
        'student': student,
        'summary': summary,
        'activities': activities,
        'certificates': certificates,
        'internships': internships,
    }
    return render(request, 'Faculty/MonitorStudent.html', context)

def MyProfile(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    return render(request, 'Faculty/MyProfile.html', {'faculty': faculty})

def EditProfile(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    if request.method == "POST":
        faculty.faculty_name = request.POST.get("txt_name")
        faculty.faculty_email = request.POST.get("txt_email")
        faculty.faculty_contact = request.POST.get("txt_contact")
        faculty.faculty_address = request.POST.get("txt_address")
        if request.FILES.get("photo"):
            faculty.faculty_photo = request.FILES.get("photo")
        faculty.save()
        log_action(faculty.faculty_name, 'Faculty', 'Updated Profile', 'Profile')
        return redirect('Faculty:MyProfile')

    return render(request, 'Faculty/EditProfile.html', {'faculty': faculty})

def ChangePassword(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    msg = None
    if request.method == "POST":
        old_pass = request.POST.get("txt_old")
        new_pass = request.POST.get("txt_new")
        confirm_pass = request.POST.get("txt_confirm")

        if faculty.faculty_password == old_pass:
            if new_pass == confirm_pass:
                faculty.faculty_password = new_pass
                faculty.save()
                msg = "Password updated successfully!"
            else:
                msg = "New passwords do not match."
        else:
            msg = "Current password incorrect."

    return render(request, 'Faculty/ChangePassword.html', {'msg': msg})

# ==================== NEW EDUTRACK-X FACULTY VIEWS ====================

# 1. Activity Approvals
def ActivityApprovals(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    assigned_students = tbl_student.objects.filter(assigned_faculty=faculty)
    
    pending_registrations = tbl_studentactivity.objects.filter(student__in=assigned_students, status__in=[0, 1]).select_related('student', 'activity', 'activity__category').order_by('-id')
    all_registrations = tbl_studentactivity.objects.filter(student__in=assigned_students).select_related('student', 'activity', 'activity__category').order_by('-id')

    return render(request, 'Faculty/ActivityApprovals.html', {
        'pending_registrations': pending_registrations,
        'all_registrations': all_registrations
    })

def ApproveActivityAction(request, rid, status):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    reg = tbl_studentactivity.objects.get(id=rid, student__assigned_faculty=faculty)
    remark = request.POST.get("txt_remark", "").strip() if request.method == "POST" else ""

    reg.status = status # 2: Approved, 3: Rejected
    if remark:
        reg.faculty_remark = remark
    reg.save()

    status_text = "approved" if status == 2 else "rejected"
    create_notification('student', reg.student.id, 'Activity Registration Update', f"Your registration for '{reg.activity.activity_title}' was {status_text}.")
    log_action(faculty.faculty_name, 'Faculty', f"{status_text.capitalize()} Activity Registration", 'Academic Activity', reg.id)

    return redirect('Faculty:ActivityApprovals')


# 2. Certificate Verification & Automatic Credit Generation Workflow
def CertificateVerifications(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    assigned_students = tbl_student.objects.filter(assigned_faculty=faculty)

    pending_certs = tbl_certificate.objects.filter(student__in=assigned_students, status=0).select_related('student', 'activity_category', 'related_activity').order_by('-id')
    all_certs = tbl_certificate.objects.filter(student__in=assigned_students).select_related('student', 'activity_category', 'related_activity').order_by('-id')

    return render(request, 'Faculty/CertificateVerifications.html', {
        'pending_certs': pending_certs,
        'all_certs': all_certs
    })

def VerifyCertificateAction(request, cid):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    cert = tbl_certificate.objects.get(id=cid, student__assigned_faculty=faculty)

    if request.method == "POST":
        action = request.POST.get("sel_action") # 'approve', 'reject', 'resubmit'
        remarks = request.POST.get("txt_remarks", "").strip()
        credit_val = request.POST.get("txt_credit_value", "0").strip()

        from datetime import date
        cert.faculty = faculty
        cert.verification_date = date.today()
        cert.faculty_remarks = remarks

        if action == 'approve':
            c_val = int(credit_val) if credit_val.isdigit() else cert.activity_category.default_credit
            cert.status = 1 # Approved
            cert.confirmed_credit = c_val
            cert.save()

            # AUTOMATIC CREDIT GENERATION (Idempotent check)
            existing_credit = tbl_studentcredit.objects.filter(
                student=cert.student,
                source_type='Certificate',
                source_reference=str(cert.id)
            ).first()

            if not existing_credit:
                tbl_studentcredit.objects.create(
                    student=cert.student,
                    credit_category=cert.activity_category,
                    credit_type=cert.certificate_title,
                    credit_value=c_val,
                    source_type='Certificate',
                    source_reference=str(cert.id),
                    semester=cert.student.programme.programme_duration if cert.student.programme else 1,
                    approval_status=1, # Approved
                    approved_by=faculty,
                    approval_date=date.today(),
                    remarks=f"Awarded for certificate: {cert.certificate_title}"
                )

            if cert.related_activity:
                cert.related_activity.status = 6 # Credit Awarded
                cert.related_activity.save()

            create_notification('student', cert.student.id, 'Certificate Approved', f"Your certificate '{cert.certificate_title}' has been approved and {c_val} credits awarded!")
            log_action(faculty.faculty_name, 'Faculty', 'Approved Certificate & Awarded Credit', 'Certificate Management', cert.id)

        elif action == 'reject':
            cert.status = 2 # Rejected
            cert.save()
            create_notification('student', cert.student.id, 'Certificate Rejected', f"Your certificate '{cert.certificate_title}' was rejected. Remark: {remarks}")
            log_action(faculty.faculty_name, 'Faculty', 'Rejected Certificate', 'Certificate Management', cert.id)

        elif action == 'resubmit':
            cert.status = 3 # Resubmission Required
            cert.save()
            create_notification('student', cert.student.id, 'Certificate Resubmission Requested', f"Please resubmit certificate '{cert.certificate_title}'. Remark: {remarks}")
            log_action(faculty.faculty_name, 'Faculty', 'Requested Certificate Resubmission', 'Certificate Management', cert.id)

        return redirect('Faculty:CertificateVerifications')

    return render(request, 'Faculty/VerifyCertificateAction.html', {'cert': cert})


# 3. Internship Monitoring & Evaluation Workflow
def InternshipMonitoring(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    assigned_students = tbl_student.objects.filter(assigned_faculty=faculty)

    internships = tbl_internship.objects.filter(student__in=assigned_students).select_related('student', 'company', 'opportunity').order_by('-id')
    progress_reports = tbl_internshipprogress.objects.filter(student__in=assigned_students).select_related('student', 'internship').order_by('-id')
    final_reports = tbl_internshipreport.objects.filter(student__in=assigned_students).select_related('student', 'internship').order_by('-id')

    return render(request, 'Faculty/InternshipMonitoring.html', {
        'internships': internships,
        'progress_reports': progress_reports,
        'final_reports': final_reports
    })

def StudentAttendance(request, iid):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    internship = tbl_internship.objects.get(id=iid, student__assigned_faculty=faculty)

    attendance_records = tbl_internshipattendance.objects.filter(internship=internship).order_by('-attendance_date')

    total_days = attendance_records.count()
    present_days = attendance_records.filter(attendance_status=1).count()
    absent_days = attendance_records.filter(attendance_status=0).count()
    half_days = attendance_records.filter(attendance_status=2).count()
    leave_days = attendance_records.filter(attendance_status=3).count()
    verified_days = attendance_records.filter(verification_status=1).count()

    total_hours = sum([float(r.hours_worked) for r in attendance_records if r.hours_worked])
    total_hours = round(total_hours, 2)

    effective_present = present_days + (half_days * 0.5)
    attendance_rate = round((effective_present / total_days * 100), 1) if total_days > 0 else 0

    stats = {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'half_days': half_days,
        'leave_days': leave_days,
        'verified_days': verified_days,
        'total_hours': total_hours,
        'attendance_rate': attendance_rate,
    }

    return render(request, 'Faculty/StudentAttendance.html', {
        'faculty': faculty,
        'internship': internship,
        'attendance_records': attendance_records,
        'stats': stats,
    })

def ReviewProgressReport(request, pid):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    report = tbl_internshipprogress.objects.get(id=pid, student__assigned_faculty=faculty)

    if request.method == "POST":
        remark = request.POST.get("txt_faculty_remark", "").strip()
        report.faculty_remark = remark
        report.progress_status = 1 # Reviewed
        report.save()

        create_notification('student', report.student.id, 'Internship Progress Reviewed', f"Faculty guide reviewed your progress report for {report.reporting_date}.")
        log_action(faculty.faculty_name, 'Faculty', 'Reviewed Internship Progress Report', 'Internship Progress', report.id)
        return redirect('Faculty:InternshipMonitoring')

    return render(request, 'Faculty/ReviewProgressReport.html', {'report': report})

def EvaluateInternship(request, iid):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    internship = tbl_internship.objects.get(id=iid, student__assigned_faculty=faculty)
    company_eval = tbl_companyevaluation.objects.filter(internship=internship).first()
    final_report = tbl_internshipreport.objects.filter(internship=internship).first()

    # Calculate real-time attendance stats for faculty evaluation
    attendance_records = tbl_internshipattendance.objects.filter(internship=internship)
    total_days = attendance_records.count()
    present_days = attendance_records.filter(attendance_status=1).count()
    half_days = attendance_records.filter(attendance_status=2).count()
    total_hours = round(sum([float(r.hours_worked) for r in attendance_records if r.hours_worked]), 2)
    att_rate = round(((present_days + (half_days * 0.5)) / total_days * 100), 1) if total_days > 0 else 0
    att_stats = {
        'total_days': total_days,
        'present_days': present_days,
        'total_hours': total_hours,
        'attendance_rate': att_rate,
    }

    if request.method == "POST":
        marks = request.POST.get("txt_marks", "100").strip()
        remark = request.POST.get("txt_faculty_remark", "").strip()
        credit_val = request.POST.get("txt_credit_value", "2").strip()
        action = request.POST.get("sel_action", "approve")

        from datetime import date
        c_val = int(credit_val) if credit_val.isdigit() else 2

        if action == "approve":
            internship.internship_status = 7 # Completed
            internship.evaluation_marks = int(marks) if marks.isdigit() else 100
            internship.evaluation_remark = remark
            internship.credits_awarded = c_val
            internship.actual_completion_date = date.today()
            internship.save()

            if final_report:
                final_report.faculty_status = 2 # Approved
                final_report.faculty_remark = remark
                final_report.save()

            # AUTOMATIC INTERNSHIP CREDIT GENERATION (Idempotent check)
            existing_credit = tbl_studentcredit.objects.filter(
                student=internship.student,
                source_type='Internship',
                source_reference=str(internship.id)
            ).first()

            if not existing_credit:
                cat = tbl_activitycategory.objects.filter(category_name__icontains='Internship').first()
                tbl_studentcredit.objects.create(
                    student=internship.student,
                    credit_category=cat,
                    credit_type=f"Internship - {internship.company.company_name}",
                    credit_value=c_val,
                    source_type='Internship',
                    source_reference=str(internship.id),
                    semester=internship.student.programme.programme_duration if internship.student.programme else 1,
                    approval_status=1, # Approved
                    approved_by=faculty,
                    approval_date=date.today(),
                    remarks=f"Internship completion evaluated at {internship.company.company_name}"
                )

            create_notification('student', internship.student.id, 'Internship Completed & Credits Awarded', f"Your internship at {internship.company.company_name} is finalized! {c_val} credits awarded.")
            create_notification('company', internship.company.id, 'Internship Completed', f"Faculty finalized internship evaluation for intern {internship.student.student_name}.")
            log_action(faculty.faculty_name, 'Faculty', 'Finalized Internship & Awarded Credits', 'Internship', internship.id)

        return redirect('Faculty:InternshipMonitoring')

    return render(request, 'Faculty/EvaluateInternship.html', {
        'internship': internship,
        'company_eval': company_eval,
        'final_report': final_report,
        'att_stats': att_stats,
    })


# 4. Credit Approvals, Notifications & Reports
def CreditApproval(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    assigned_students = tbl_student.objects.filter(assigned_faculty=faculty)

    credits_list = tbl_studentcredit.objects.filter(student__in=assigned_students).select_related('student', 'credit_category', 'approved_by').order_by('-credit_date')
    return render(request, 'Faculty/CreditApproval.html', {'credits_list': credits_list})

def Notifications(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    notifications = tbl_notification.objects.filter(recipient_role='faculty', recipient_id__in=[faculty.id, 0]).order_by('-created_at')
    notifications.update(is_read=True)

    return render(request, 'Faculty/Notifications.html', {'notifications': notifications})

def Reports(request):
    if 'fid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=request.session['fid'])
    students = tbl_student.objects.filter(assigned_faculty=faculty)

    student_data = []
    for s in students:
        summary = get_student_credit_summary(s.id)
        student_data.append({
            'student': s,
            'summary': summary
        })

    return render(request, 'Faculty/Reports.html', {
        'faculty': faculty,
        'student_data': student_data
    })


