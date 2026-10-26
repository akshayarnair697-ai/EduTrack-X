from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from Administrator.models import tbl_adminregistration, tbl_department, tbl_programme, tbl_batch, tbl_academicyear, tbl_activitycategory, tbl_academicactivity, tbl_creditrequirement, tbl_notification, tbl_auditlog
from Guest.models import tbl_student, tbl_faculty, tbl_company
from Student.models import tbl_studentcredit
from Administrator.utils import create_notification, log_action, get_student_credit_summary

def Dashboard(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    total_companies = tbl_company.objects.count()
    pending_companies = tbl_company.objects.filter(company_status=0).count()
    total_students = tbl_student.objects.count()
    pending_students = tbl_student.objects.filter(student_status=0).count()
    total_faculty = tbl_faculty.objects.count()
    pending_faculty = tbl_faculty.objects.filter(faculty_status=0).count()
    total_departments = tbl_department.objects.count()
    total_programmes = tbl_programme.objects.count()

    context = {
        'total_companies': total_companies,
        'pending_companies': pending_companies,
        'total_students': total_students,
        'pending_students': pending_students,
        'total_faculty': total_faculty,
        'pending_faculty': pending_faculty,
        'total_departments': total_departments,
        'total_programmes': total_programmes,
    }
    return render(request, 'Administrator/Dashboard.html', context)

def VerifyCompanies(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    pending_companies = tbl_company.objects.filter(company_status=0).order_by('-id')
    all_companies = tbl_company.objects.all().order_by('-id')
    return render(request, 'Administrator/VerifyCompanies.html', {'pending_companies': pending_companies, 'all_companies': all_companies})

def ApproveCompanyAction(request, cid, status):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=cid)
    company.company_status = status
    company.save()
    return redirect('Administrator:VerifyCompanies')

def VerifyStudents(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    pending_students = tbl_student.objects.filter(student_status=0).order_by('-id')
    all_students = tbl_student.objects.all().order_by('-id')
    return render(request, 'Administrator/VerifyStudents.html', {'pending_students': pending_students, 'all_students': all_students})

def ApproveStudentAction(request, sid, status):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=sid)
    student.student_status = status
    student.save()
    return redirect('Administrator:VerifyStudents')

def VerifyFaculties(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    pending_faculty = tbl_faculty.objects.filter(faculty_status=0).order_by('-id')
    all_faculties = tbl_faculty.objects.all().order_by('-id')
    return render(request, 'Administrator/VerifyFaculties.html', {'pending_faculty': pending_faculty, 'all_faculties': all_faculties})

import random

def generate_faculty_password(name, dept_name):
    clean_name = ''.join(c for c in name if c.isalnum()).upper()[:4]
    clean_dept = ''.join(c for c in dept_name if c.isalnum()).upper()[:3]
    rand_code = random.randint(1000, 9999)
    return f"{clean_name}@{clean_dept}{rand_code}"

def AddFaculty(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    departments = tbl_department.objects.all()

    if request.method == "POST":
        name = request.POST.get("txt_name")
        email = request.POST.get("txt_email")
        contact = request.POST.get("txt_contact")
        address = request.POST.get("txt_address")
        department_id = request.POST.get("sel_department")
        password = request.POST.get("txt_password")
        photo = request.FILES.get("photo")

        dept = tbl_department.objects.get(id=department_id)

        if not password:
            password = generate_faculty_password(name, dept.department_name)

        tbl_faculty.objects.create(
            department=dept,
            faculty_name=name,
            faculty_email=email,
            faculty_contact=contact,
            faculty_address=address,
            faculty_password=password,
            faculty_status=1,
            faculty_photo=photo
        )
        create_notification('faculty', 0, 'Welcome to EduTrack', f"Faculty account created for {name}.")
        log_action(request.session.get('name', 'Admin'), 'Admin', 'Added Faculty', 'Faculty Management', description=f"Faculty {name} added")
        return redirect('Administrator:VerifyFaculties')

    return render(request, 'Administrator/AddFaculty.html', {'departments': departments})

def ApproveFacultyAction(request, fid, status):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    faculty = tbl_faculty.objects.get(id=fid)
    faculty.faculty_status = status
    faculty.save()
    return redirect('Administrator:VerifyFaculties')

def AssignFaculty(request, sid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=sid)
    department = student.programme.department
    dept_faculties = tbl_faculty.objects.filter(department=department, faculty_status=1)

    return render(request, 'Administrator/AssignFaculty.html', {
        'student': student,
        'department': department,
        'dept_faculties': dept_faculties,
    })

def AssignFacultyAction(request, sid, fid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    student = tbl_student.objects.get(id=sid)
    faculty = tbl_faculty.objects.get(id=fid)
    student.assigned_faculty = faculty
    student.save()
    return redirect('Administrator:VerifyStudents')

# Master Data CRUD Operations

def Department(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    departments = tbl_department.objects.all()
    if request.method == "POST":
        dept_name = request.POST.get("txt_department")
        if dept_name:
            tbl_department.objects.create(department_name=dept_name)
            return redirect('Administrator:Department')

    return render(request, 'Administrator/Department.html', {'departments': departments})

def edit_department(request, did):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    dept = tbl_department.objects.get(id=did)
    departments = tbl_department.objects.all()
    if request.method == "POST":
        dept_name = request.POST.get("txt_department")
        if dept_name:
            dept.department_name = dept_name
            dept.save()
            return redirect('Administrator:Department')

    return render(request, 'Administrator/Department.html', {'dept_edit': dept, 'departments': departments})

def del_department(request, did):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    tbl_department.objects.get(id=did).delete()
    return redirect('Administrator:Department')

def Programme(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    programmes = tbl_programme.objects.all()
    departments = tbl_department.objects.all()

    if request.method == "POST":
        pname = request.POST.get("txt_programme")
        pduration = request.POST.get("txt_duration")
        pcredit = request.POST.get("txt_credit")
        dept_id = request.POST.get("sel_department")

        if pname and pduration and pcredit and dept_id:
            dept = tbl_department.objects.get(id=dept_id)
            tbl_programme.objects.create(
                programme_name=pname,
                programme_duration=pduration,
                programme_totalcredit=pcredit,
                department=dept
            )
            return redirect('Administrator:Programme')

    return render(request, 'Administrator/Programme.html', {'programmes': programmes, 'departments': departments})

def edit_programme(request, pid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    prog = tbl_programme.objects.get(id=pid)
    programmes = tbl_programme.objects.all()
    departments = tbl_department.objects.all()

    if request.method == "POST":
        pname = request.POST.get("txt_programme")
        pduration = request.POST.get("txt_duration")
        pcredit = request.POST.get("txt_credit")
        dept_id = request.POST.get("sel_department")

        if pname and pduration and pcredit and dept_id:
            dept = tbl_department.objects.get(id=dept_id)
            prog.programme_name = pname
            prog.programme_duration = pduration
            prog.programme_totalcredit = pcredit
            prog.department = dept
            prog.save()
            return redirect('Administrator:Programme')

    return render(request, 'Administrator/Programme.html', {'prog_edit': prog, 'programmes': programmes, 'departments': departments})

def del_programme(request, did):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    tbl_programme.objects.get(id=did).delete()
    return redirect('Administrator:Programme')

def AcademicYear(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    years = tbl_academicyear.objects.all()
    if request.method == "POST":
        year_name = request.POST.get("txt_academicyear")
        if year_name:
            tbl_academicyear.objects.create(academicyear_name=year_name)
            return redirect('Administrator:AcademicYear')

    return render(request, 'Administrator/AcademicYear.html', {'years': years})

def del_academicyear(request, yid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    tbl_academicyear.objects.get(id=yid).delete()
    return redirect('Administrator:AcademicYear')

def Batch(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    batches = tbl_batch.objects.all()
    if request.method == "POST":
        batch_name = request.POST.get("txt_batch")
        if batch_name:
            tbl_batch.objects.create(batch_name=batch_name)
            return redirect('Administrator:Batch')

    return render(request, 'Administrator/Batch.html', {'batches': batches})

def del_batch(request, bid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    tbl_batch.objects.get(id=bid).delete()
    return redirect('Administrator:Batch')

# ==================== NEW EDUTRACK-X MODULES ====================

# 1. Activity Category Management
def ActivityCategory(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    categories = tbl_activitycategory.objects.all().order_by('-id')
    if request.method == "POST":
        cname = request.POST.get("txt_category_name", "").strip()
        cdesc = request.POST.get("txt_description", "").strip()
        def_credit = request.POST.get("txt_default_credit", "0").strip()

        if cname:
            tbl_activitycategory.objects.create(
                category_name=cname,
                description=cdesc,
                default_credit=int(def_credit) if def_credit.isdigit() else 0
            )
            log_action(request.session.get('name', 'Admin'), 'Admin', 'Created Activity Category', 'Academic Activity', description=f"Category: {cname}")
            return redirect('Administrator:ActivityCategory')

    return render(request, 'Administrator/ActivityCategory.html', {'categories': categories})

def edit_activitycategory(request, cid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    category = tbl_activitycategory.objects.get(id=cid)
    categories = tbl_activitycategory.objects.all().order_by('-id')

    if request.method == "POST":
        cname = request.POST.get("txt_category_name", "").strip()
        cdesc = request.POST.get("txt_description", "").strip()
        def_credit = request.POST.get("txt_default_credit", "0").strip()

        if cname:
            category.category_name = cname
            category.description = cdesc
            category.default_credit = int(def_credit) if def_credit.isdigit() else 0
            category.save()
            log_action(request.session.get('name', 'Admin'), 'Admin', 'Updated Activity Category', 'Academic Activity', cid, f"Category: {cname}")
            return redirect('Administrator:ActivityCategory')

    return render(request, 'Administrator/ActivityCategory.html', {'cat_edit': category, 'categories': categories})

def toggle_activitycategory(request, cid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    category = tbl_activitycategory.objects.get(id=cid)
    category.status = 0 if category.status == 1 else 1
    category.save()
    log_action(request.session.get('name', 'Admin'), 'Admin', 'Toggled Activity Category Status', 'Academic Activity', cid)
    return redirect('Administrator:ActivityCategory')


# 2. Credit Requirement Configurator
def CreditRequirement(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    programmes = tbl_programme.objects.all()
    categories = tbl_activitycategory.objects.filter(status=1)
    years = tbl_academicyear.objects.all()
    requirements = tbl_creditrequirement.objects.select_related('programme', 'activity_category', 'academic_year').order_by('-id')

    if request.method == "POST":
        programme_id = request.POST.get("sel_programme")
        category_id = request.POST.get("sel_category")
        year_id = request.POST.get("sel_year")
        semester = request.POST.get("sel_semester")
        req_credit = request.POST.get("txt_req_credit", "0").strip()

        if programme_id and category_id and req_credit:
            prog = tbl_programme.objects.get(id=programme_id)
            cat = tbl_activitycategory.objects.get(id=category_id)
            year_obj = tbl_academicyear.objects.get(id=year_id) if year_id else None
            sem_val = int(semester) if semester and semester.isdigit() else None

            tbl_creditrequirement.objects.create(
                programme=prog,
                activity_category=cat,
                academic_year=year_obj,
                semester=sem_val,
                required_credit=int(req_credit) if req_credit.isdigit() else 0
            )
            log_action(request.session.get('name', 'Admin'), 'Admin', 'Created Credit Requirement', 'Credit Requirement', description=f"{prog.programme_name} - {cat.category_name}: {req_credit} Credits")
            return redirect('Administrator:CreditRequirement')

    return render(request, 'Administrator/CreditRequirement.html', {
        'programmes': programmes,
        'categories': categories,
        'years': years,
        'requirements': requirements
    })

def del_creditrequirement(request, rid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    tbl_creditrequirement.objects.filter(id=rid).delete()
    return redirect('Administrator:CreditRequirement')


# 3. Academic Activity Management
def AcademicActivity(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    categories = tbl_activitycategory.objects.filter(status=1)
    years = tbl_academicyear.objects.all()
    programmes = tbl_programme.objects.all()
    batches = tbl_batch.objects.all()
    activities = tbl_academicactivity.objects.all().order_by('-id')

    if request.method == "POST":
        title = request.POST.get("txt_title", "").strip()
        category_id = request.POST.get("sel_category")
        desc = request.POST.get("txt_description", "").strip()
        org = request.POST.get("txt_org", "").strip()
        start_date = request.POST.get("txt_start_date")
        end_date = request.POST.get("txt_end_date")
        duration = request.POST.get("txt_duration", "").strip()
        year_id = request.POST.get("sel_year")
        semester = request.POST.get("txt_semester", "1").strip()
        prog_id = request.POST.get("sel_programme")
        batch_id = request.POST.get("sel_batch")
        max_p = request.POST.get("txt_max_participants", "").strip()
        deadline = request.POST.get("txt_deadline")
        credit_val = request.POST.get("txt_credit_value", "0").strip()
        proof = request.POST.get("txt_proof", "Certificate").strip()

        if title and category_id and start_date and deadline:
            cat = tbl_activitycategory.objects.get(id=category_id)
            year_obj = tbl_academicyear.objects.get(id=year_id) if year_id else tbl_academicyear.objects.first()
            prog_obj = tbl_programme.objects.get(id=prog_id) if prog_id else None
            batch_obj = tbl_batch.objects.get(id=batch_id) if batch_id else None

            act_obj = tbl_academicactivity.objects.create(
                activity_title=title,
                category=cat,
                description=desc,
                conducting_org=org,
                start_date=start_date,
                end_date=end_date or start_date,
                duration=duration or "1 Day",
                academic_year=year_obj,
                semester=int(semester) if semester.isdigit() else 1,
                eligible_programme=prog_obj,
                eligible_batch=batch_obj,
                max_participants=int(max_p) if max_p.isdigit() else None,
                registration_deadline=deadline,
                credit_value=int(credit_val) if credit_val.isdigit() else 0,
                required_proof=proof,
                activity_status=1 # Open for registration
            )

            # Send notification to eligible students
            create_notification('student', 0, 'New Academic Activity Available', f"Activity '{title}' is open for registration!")
            log_action(request.session.get('name', 'Admin'), 'Admin', 'Created Academic Activity', 'Academic Activity', act_obj.id, f"Title: {title}")
            return redirect('Administrator:AcademicActivity')

    return render(request, 'Administrator/AcademicActivity.html', {
        'categories': categories,
        'years': years,
        'programmes': programmes,
        'batches': batches,
        'activities': activities
    })

def edit_academicactivity(request, aid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    activity = tbl_academicactivity.objects.get(id=aid)
    categories = tbl_activitycategory.objects.filter(status=1)
    years = tbl_academicyear.objects.all()
    programmes = tbl_programme.objects.all()
    batches = tbl_batch.objects.all()
    activities = tbl_academicactivity.objects.all().order_by('-id')

    if request.method == "POST":
        title = request.POST.get("txt_title", "").strip()
        category_id = request.POST.get("sel_category")
        desc = request.POST.get("txt_description", "").strip()
        org = request.POST.get("txt_org", "").strip()
        start_date = request.POST.get("txt_start_date")
        end_date = request.POST.get("txt_end_date")
        duration = request.POST.get("txt_duration", "").strip()
        year_id = request.POST.get("sel_year")
        semester = request.POST.get("txt_semester", "1").strip()
        prog_id = request.POST.get("sel_programme")
        batch_id = request.POST.get("sel_batch")
        max_p = request.POST.get("txt_max_participants", "").strip()
        deadline = request.POST.get("txt_deadline")
        credit_val = request.POST.get("txt_credit_value", "0").strip()
        proof = request.POST.get("txt_proof", "Certificate").strip()

        if title and category_id and start_date and deadline:
            activity.activity_title = title
            activity.category = tbl_activitycategory.objects.get(id=category_id)
            activity.description = desc
            activity.conducting_org = org
            activity.start_date = start_date
            activity.end_date = end_date or start_date
            activity.duration = duration
            if year_id:
                activity.academic_year = tbl_academicyear.objects.get(id=year_id)
            activity.semester = int(semester) if semester.isdigit() else 1
            activity.eligible_programme = tbl_programme.objects.get(id=prog_id) if prog_id else None
            activity.eligible_batch = tbl_batch.objects.get(id=batch_id) if batch_id else None
            activity.max_participants = int(max_p) if max_p.isdigit() else None
            activity.registration_deadline = deadline
            activity.credit_value = int(credit_val) if credit_val.isdigit() else 0
            activity.required_proof = proof
            activity.save()
            return redirect('Administrator:AcademicActivity')

    return render(request, 'Administrator/AcademicActivity.html', {
        'act_edit': activity,
        'categories': categories,
        'years': years,
        'programmes': programmes,
        'batches': batches,
        'activities': activities
    })

def update_activity_status(request, aid, status):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    activity = tbl_academicactivity.objects.get(id=aid)
    activity.activity_status = status
    activity.save()
    return redirect('Administrator:AcademicActivity')

def ViewActivityRegistrations(request, aid):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    activity = tbl_academicactivity.objects.get(id=aid)
    from Student.models import tbl_studentactivity
    registrations = tbl_studentactivity.objects.filter(activity=activity).select_related('student').order_by('-id')
    return render(request, 'Administrator/ViewActivityRegistrations.html', {'activity': activity, 'registrations': registrations})


# 4. Student Progress Monitoring
def StudentProgressMonitoring(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    departments = tbl_department.objects.all()
    programmes = tbl_programme.objects.all()
    batches = tbl_batch.objects.all()

    students = tbl_student.objects.filter(student_status=1).select_related('programme', 'batch', 'programme__department')

    dept_id = request.GET.get('dept')
    prog_id = request.GET.get('prog')
    batch_id = request.GET.get('batch')
    search_q = request.GET.get('q')

    if dept_id:
        students = students.filter(programme__department_id=dept_id)
    if prog_id:
        students = students.filter(programme_id=prog_id)
    if batch_id:
        students = students.filter(batch_id=batch_id)
    if search_q:
        students = students.filter(student_name__icontains=search_q)

    student_metrics = []
    for s in students:
        summary = get_student_credit_summary(s.id)
        student_metrics.append({
            'student': s,
            'summary': summary
        })

    return render(request, 'Administrator/StudentProgressMonitoring.html', {
        'departments': departments,
        'programmes': programmes,
        'batches': batches,
        'student_metrics': student_metrics
    })


# 5. Certificate & Internship Overviews
def CertificateMonitoring(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    from Student.models import tbl_certificate
    certificates = tbl_certificate.objects.select_related('student', 'activity_category', 'faculty').order_by('-id')

    status_filter = request.GET.get('status')
    if status_filter is not None and status_filter != "":
        certificates = certificates.filter(status=int(status_filter))

    total_count = certificates.count()
    approved_count = tbl_certificate.objects.filter(status=1).count()
    pending_count = tbl_certificate.objects.filter(status=0).count()
    rejected_count = tbl_certificate.objects.filter(status=2).count()

    return render(request, 'Administrator/CertificateMonitoring.html', {
        'certificates': certificates,
        'total_count': total_count,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count
    })

def InternshipMonitoring(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    from Company.models import tbl_internship, tbl_opportunity
    internships = tbl_internship.objects.select_related('student', 'company', 'opportunity', 'faculty').order_by('-id')

    status_filter = request.GET.get('status')
    if status_filter is not None and status_filter != "":
        internships = internships.filter(internship_status=int(status_filter))

    total_opps = tbl_opportunity.objects.count()
    total_apps = tbl_internship.objects.count()
    active_interns = tbl_internship.objects.filter(internship_status__in=[3, 4, 5, 6]).count()
    completed_interns = tbl_internship.objects.filter(internship_status=7).count()

    return render(request, 'Administrator/InternshipMonitoring.html', {
        'internships': internships,
        'total_opps': total_opps,
        'total_apps': total_apps,
        'active_interns': active_interns,
        'completed_interns': completed_interns
    })


# 6. Notifications, Audit Logs & Reports
def Notifications(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    from Administrator.models import tbl_notification
    notifications = tbl_notification.objects.filter(recipient_role__in=['admin', 'all']).order_by('-created_at')
    # Mark as read
    notifications.update(is_read=True)

    return render(request, 'Administrator/Notifications.html', {'notifications': notifications})

def AuditLogs(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    from Administrator.models import tbl_auditlog
    logs = tbl_auditlog.objects.all().order_by('-timestamp')[:200]
    return render(request, 'Administrator/AuditLogs.html', {'logs': logs})

def Reports(request):
    if 'aid' not in request.session:
        return redirect('Guest:Login')

    from Administrator.models import tbl_academicactivity
    from Company.models import tbl_internship

    departments = tbl_department.objects.all()
    programmes = tbl_programme.objects.all()

    report_type = request.GET.get('type', 'summary')
    prog_id = request.GET.get('prog')

    students_list = tbl_student.objects.filter(student_status=1)
    if prog_id:
        students_list = students_list.filter(programme_id=prog_id)

    student_data = []
    for s in students_list:
        summary = get_student_credit_summary(s.id)
        student_data.append({
            'student': s,
            'summary': summary
        })

    return render(request, 'Administrator/Reports.html', {
        'departments': departments,
        'programmes': programmes,
        'student_data': student_data,
        'report_type': report_type,
        'selected_prog': int(prog_id) if prog_id else None
    })

