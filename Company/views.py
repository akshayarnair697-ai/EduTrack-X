from datetime import datetime, date
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from Company.models import (
    tbl_opportunity, tbl_internship, tbl_studymaterial, tbl_task,
    tbl_internshipprogress, tbl_internshipreport, tbl_companyevaluation,
    tbl_internshipattendance
)
from Guest.models import tbl_company, tbl_student
from Administrator.models import tbl_notification
from Administrator.utils import create_notification, log_action

def Dashboard(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    total_posted = tbl_opportunity.objects.filter(company=company).count()
    app_count = tbl_internship.objects.filter(company=company).count()
    accepted_count = tbl_internship.objects.filter(company=company, internship_status=1).count()

    context = {
        'company': company,
        'total_posted': total_posted,
        'app_count': app_count,
        'accepted_count': accepted_count,
    }
    return render(request, 'Company/Dashboard.html', context)

def PostOpportunity(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    if request.method == "POST":
        tbl_opportunity.objects.create(
            company=company,
            opportunity_title=request.POST.get("txt_title"),
            opportunity_description=request.POST.get("txt_description"),
            skills_required=request.POST.get("txt_skills"),
            duration=request.POST.get("txt_duration"),
            stipend=request.POST.get("txt_stipend", "Unpaid"),
            last_date=request.POST.get("txt_last_date")
        )
        return redirect('Company:ViewOpportunities')

    return render(request, 'Company/PostOpportunity.html', {'company': company})

def ViewOpportunities(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    opportunities = tbl_opportunity.objects.filter(company=company).order_by('-id')
    return render(request, 'Company/ViewOpportunities.html', {'opportunities': opportunities})

def EditOpportunity(request, oid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    opportunity = tbl_opportunity.objects.get(id=oid, company=company)
    if request.method == "POST":
        opportunity.opportunity_title = request.POST.get("txt_title")
        opportunity.opportunity_description = request.POST.get("txt_description")
        opportunity.skills_required = request.POST.get("txt_skills")
        opportunity.duration = request.POST.get("txt_duration")
        opportunity.stipend = request.POST.get("txt_stipend", "Unpaid")
        opportunity.last_date = request.POST.get("txt_last_date")
        opportunity.save()
        return redirect('Company:ViewOpportunities')

    return render(request, 'Company/EditOpportunity.html', {'opportunity': opportunity})

def DelOpportunity(request, oid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    tbl_opportunity.objects.filter(id=oid, company=company).delete()
    return redirect('Company:ViewOpportunities')

def InternshipApplications(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    applications = tbl_internship.objects.filter(company=company).order_by('-id')
    return render(request, 'Company/InternshipApplications.html', {'applications': applications})

def UpdateApplicationStatus(request, app_id, status):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    application = tbl_internship.objects.get(id=app_id, company=company)
    application.internship_status = status
    application.save()
    return redirect('Company:InternshipApplications')

def MyProfile(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    return render(request, 'Company/MyProfile.html', {'company': company})

def EditProfile(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    if request.method == "POST":
        company.company_name = request.POST.get("txt_name")
        company.company_email = request.POST.get("txt_email")
        company.company_contact = request.POST.get("txt_contact")
        company.company_address = request.POST.get("txt_address")
        company.company_website = request.POST.get("txt_website")
        company.company_industry = request.POST.get("txt_industry")
        company.company_description = request.POST.get("txt_description")
        if request.FILES.get("logo"):
            company.company_logo = request.FILES.get("logo")
        if request.FILES.get("proof"):
            company.company_proof = request.FILES.get("proof")
        company.save()
        return redirect('Company:MyProfile')

    return render(request, 'Company/EditProfile.html', {'company': company})

def ChangePassword(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    msg = None
    if request.method == "POST":
        old_pass = request.POST.get("txt_old")
        new_pass = request.POST.get("txt_new")
        confirm_pass = request.POST.get("txt_confirm")

        if company.company_password == old_pass:
            if new_pass == confirm_pass:
                company.company_password = new_pass
                company.save()
                msg = "Password updated successfully!"
            else:
                msg = "New passwords do not match."
        else:
            msg = "Current password incorrect."

    return render(request, 'Company/ChangePassword.html', {'msg': msg})

def AddStudyMaterial(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    if request.method == "POST":
        tbl_studymaterial.objects.create(
            company=company,
            material_title=request.POST.get("txt_title"),
            material_description=request.POST.get("txt_description"),
            material_file=request.FILES.get("file_material")
        )
        return redirect('Company:ViewStudyMaterials')

    return render(request, 'Company/AddStudyMaterial.html', {'company': company})

def ViewStudyMaterials(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    materials = tbl_studymaterial.objects.filter(company=company).order_by('-id')
    return render(request, 'Company/ViewStudyMaterials.html', {'materials': materials})

def DelStudyMaterial(request, mid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    tbl_studymaterial.objects.filter(id=mid, company_id=request.session['cid']).delete()
    return redirect('Company:ViewStudyMaterials')

def AssignTask(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    accepted_internships = tbl_internship.objects.filter(company=company, internship_status__in=[1, 2, 3, 4, 5, 6, 7]).select_related('student')

    if request.method == "POST":
        student_id = request.POST.get("sel_student")
        if student_id:
            student = tbl_student.objects.get(id=student_id)
            internship = tbl_internship.objects.filter(company=company, student=student).first()
            tbl_task.objects.create(
                company=company,
                student=student,
                internship=internship,
                task_title=request.POST.get("txt_title"),
                task_description=request.POST.get("txt_description"),
                task_deadline=request.POST.get("txt_deadline"),
                task_file=request.FILES.get("file_task")
            )
            create_notification('student', student.id, 'New Task Assigned', f"Company {company.company_name} assigned task '{request.POST.get('txt_title')}' to you.")
            return redirect('Company:ViewCompanyTasks')

    return render(request, 'Company/AssignTask.html', {'accepted_internships': accepted_internships})

def ViewCompanyTasks(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    tasks = tbl_task.objects.filter(company=company).order_by('-id')
    return render(request, 'Company/ViewCompanyTasks.html', {'tasks': tasks})

def DelTask(request, tid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    tbl_task.objects.filter(id=tid, company_id=request.session['cid']).delete()
    return redirect('Company:ViewCompanyTasks')

def ManageInterns(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    interns = tbl_internship.objects.filter(company=company, internship_status__in=[1, 2, 3, 4, 5, 6, 7]).select_related('student', 'opportunity').order_by('-id')

    intern_details = []
    for i in interns:
        eval_obj = tbl_companyevaluation.objects.filter(internship=i).first()
        tasks_count = tbl_task.objects.filter(internship=i).count()
        completed_tasks = tbl_task.objects.filter(internship=i, task_status=2).count()
        intern_details.append({
            'internship': i,
            'evaluation': eval_obj,
            'tasks_count': tasks_count,
            'completed_tasks': completed_tasks
        })

    return render(request, 'Company/ManageInterns.html', {'intern_details': intern_details})

def CompanyEvaluation(request, iid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    internship = tbl_internship.objects.get(id=iid, company=company)
    eval_obj = tbl_companyevaluation.objects.filter(internship=internship).first()

    if request.method == "POST":
        tech = request.POST.get("txt_tech", "5")
        comm = request.POST.get("txt_comm", "5")
        att = request.POST.get("txt_att", "5")
        qual = request.POST.get("txt_qual", "5")
        team = request.POST.get("txt_team", "5")
        disc = request.POST.get("txt_disc", "5")
        overall = request.POST.get("txt_overall", "5")
        remarks = request.POST.get("txt_remarks", "").strip()
        confirm = request.POST.get("chk_confirm") == "on"

        if not eval_obj:
            eval_obj = tbl_companyevaluation.objects.create(
                internship=internship,
                technical_skills=int(tech),
                communication=int(comm),
                attendance=int(att),
                work_quality=int(qual),
                teamwork=int(team),
                discipline=int(disc),
                overall_performance=int(overall),
                remarks=remarks,
                confirmed_completion=confirm
            )
        else:
            eval_obj.technical_skills = int(tech)
            eval_obj.communication = int(comm)
            eval_obj.attendance = int(att)
            eval_obj.work_quality = int(qual)
            eval_obj.teamwork = int(team)
            eval_obj.discipline = int(disc)
            eval_obj.overall_performance = int(overall)
            eval_obj.remarks = remarks
            eval_obj.confirmed_completion = confirm
            eval_obj.save()

        if confirm and internship.internship_status < 6:
            internship.internship_status = 5 # Report Pending / Ready for faculty review
            internship.save()

        if internship.assigned_faculty:
            create_notification('faculty', internship.assigned_faculty.id, 'Company Evaluation Submitted', f"Company {company.company_name} evaluated intern {internship.student.student_name}.")
        create_notification('student', internship.student.id, 'Company Evaluation Received', f"{company.company_name} submitted your performance evaluation.")

        return redirect('Company:ManageInterns')

    # Real-time attendance stats for evaluation
    attendances = tbl_internshipattendance.objects.filter(internship=internship)
    total_days = attendances.count()
    present_days = attendances.filter(attendance_status=1).count()
    total_hours = sum(float(a.hours_worked) for a in attendances)
    att_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0
    att_stats = {
        'total_days': total_days,
        'present_days': present_days,
        'total_hours': round(total_hours, 2),
        'attendance_rate': att_rate
    }

    return render(request, 'Company/CompanyEvaluation.html', {
        'internship': internship, 
        'eval_obj': eval_obj,
        'att_stats': att_stats
    })

def Notifications(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    notifications = tbl_notification.objects.filter(recipient_role__iexact='company', recipient_id__in=[company.id, 0]).order_by('-created_at')
    notifications.update(is_read=True)

    return render(request, 'Company/Notifications.html', {'notifications': notifications})

def ManageAttendance(request):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    internships = tbl_internship.objects.filter(
        company=company, 
        internship_status__in=[1, 2, 3, 4, 5, 6, 7]
    ).select_related('student', 'opportunity')

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()

    if request.method == "POST":
        intern_id = request.POST.get("intern_id")
        status = int(request.POST.get("attendance_status", 1))
        hours = float(request.POST.get("hours_worked", 0.0))
        remarks = request.POST.get("company_remarks", "").strip()
        verification = int(request.POST.get("verification_status", 1))

        internship = tbl_internship.objects.filter(id=intern_id, company=company).first()
        if internship:
            att_record, created = tbl_internshipattendance.objects.get_or_create(
                internship=internship,
                attendance_date=selected_date,
                defaults={'student': internship.student}
            )
            att_record.attendance_status = status
            att_record.hours_worked = hours
            att_record.company_remarks = remarks
            att_record.verification_status = verification
            att_record.save()
        return redirect(f"{request.path}?date={selected_date.strftime('%Y-%m-%d')}")

    roster = []
    present_count = 0
    absent_count = 0
    total_day_hours = 0.0

    for i in internships:
        att = tbl_internshipattendance.objects.filter(internship=i, attendance_date=selected_date).first()
        if att:
            if att.attendance_status == 1:
                present_count += 1
            elif att.attendance_status == 0:
                absent_count += 1
            total_day_hours += float(att.hours_worked)
        roster.append({
            'internship': i,
            'attendance': att
        })

    context = {
        'company': company,
        'selected_date': selected_date,
        'roster': roster,
        'total_interns': internships.count(),
        'present_count': present_count,
        'absent_count': absent_count,
        'total_day_hours': round(total_day_hours, 2)
    }
    return render(request, 'Company/ManageAttendance.html', context)

def InternAttendance(request, iid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    internship = tbl_internship.objects.filter(id=iid, company=company).select_related('student', 'opportunity').first()
    if not internship:
        return redirect('Company:ManageInterns')

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "manual_add":
            att_date_str = request.POST.get("attendance_date")
            status = int(request.POST.get("attendance_status", 1))
            hours = float(request.POST.get("hours_worked", 0.0))
            tasks = request.POST.get("daily_tasks_summary", "").strip()
            remarks = request.POST.get("company_remarks", "").strip()
            if att_date_str:
                att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
                att, created = tbl_internshipattendance.objects.get_or_create(
                    internship=internship,
                    attendance_date=att_date,
                    defaults={'student': internship.student}
                )
                att.attendance_status = status
                att.hours_worked = hours
                if tasks:
                    att.daily_tasks_summary = tasks
                att.company_remarks = remarks
                att.verification_status = 1
                att.save()
            return redirect('Company:InternAttendance', iid=iid)

    attendances = tbl_internshipattendance.objects.filter(internship=internship).order_by('-attendance_date')
    total_days = attendances.count()
    present_days = attendances.filter(attendance_status=1).count()
    total_hours = sum(float(a.hours_worked) for a in attendances)
    att_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0

    context = {
        'company': company,
        'internship': internship,
        'attendances': attendances,
        'total_days': total_days,
        'present_days': present_days,
        'total_hours': round(total_hours, 2),
        'attendance_rate': att_rate
    }
    return render(request, 'Company/InternAttendance.html', context)

def UpdateAttendanceRecord(request, aid):
    if 'cid' not in request.session:
        return redirect('Guest:Login')

    company = tbl_company.objects.get(id=request.session['cid'])
    att = tbl_internshipattendance.objects.filter(id=aid, internship__company=company).first()
    if att and request.method == "POST":
        att.attendance_status = int(request.POST.get("attendance_status", att.attendance_status))
        att.hours_worked = float(request.POST.get("hours_worked", att.hours_worked))
        att.company_remarks = request.POST.get("company_remarks", "").strip()
        att.verification_status = int(request.POST.get("verification_status", 1))
        att.save()
    return redirect(request.META.get('HTTP_REFERER', 'Company:ManageAttendance'))

