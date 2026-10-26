from django.shortcuts import render, redirect
from Guest.models import tbl_student, tbl_faculty, tbl_company
from Administrator.models import tbl_adminregistration, tbl_department, tbl_programme, tbl_batch
from Administrator.utils import create_notification, log_action

def index(request):
    return render(request, 'Guest/index.html')

def Login(request):
    if request.method == "POST":
        email = request.POST.get("txt_email", "").strip()
        password = request.POST.get("txt_password", "").strip()

        if not email or not password:
            return render(request, 'Guest/Login.html', {'error': 'Please provide both email and password.'})

        # 1. Admin Login Check
        admin = tbl_adminregistration.objects.filter(adminregistration_email=email, adminregistration_password=password).first()
        if admin:
            request.session['aid'] = admin.id
            request.session['name'] = admin.adminregistration_name
            return redirect('Administrator:Dashboard')

        # 2. Student Login Check
        student = tbl_student.objects.filter(student_email=email, student_password=password).first()
        if student:
            if student.student_status == 1:
                request.session['sid'] = student.id
                request.session['name'] = student.student_name
                return redirect('Student:Dashboard')
            elif student.student_status == 0:
                return render(request, 'Guest/Login.html', {'error': 'Your account is pending admin verification.'})
            else:
                return render(request, 'Guest/Login.html', {'error': 'Your registration was rejected by administration.'})

        # 3. Faculty Login Check
        faculty = tbl_faculty.objects.filter(faculty_email=email, faculty_password=password).first()
        if faculty:
            if faculty.faculty_status == 1:
                request.session['fid'] = faculty.id
                request.session['name'] = faculty.faculty_name
                return redirect('Faculty:Dashboard')
            elif faculty.faculty_status == 0:
                return render(request, 'Guest/Login.html', {'error': 'Your faculty account is pending approval.'})
            else:
                return render(request, 'Guest/Login.html', {'error': 'Your registration was rejected.'})

        # 4. Company Login Check
        company = tbl_company.objects.filter(company_email=email, company_password=password).first()
        if company:
            if company.company_status == 1:
                request.session['cid'] = company.id
                request.session['name'] = company.company_name
                return redirect('Company:Dashboard')
            elif company.company_status == 0:
                return render(request, 'Guest/Login.html', {'error': 'Your company account is pending approval.'})
            else:
                return render(request, 'Guest/Login.html', {'error': 'Your registration was rejected.'})

        return render(request, 'Guest/Login.html', {'error': 'Invalid Email or Password.'})

    return render(request, 'Guest/Login.html')

def StudentRegister(request):
    programmes = tbl_programme.objects.all()
    batches = tbl_batch.objects.all()
    if request.method == "POST":
        regno = request.POST.get("txt_regno", "").strip()
        name = request.POST.get("txt_name", "").strip()
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        email = request.POST.get("txt_email", "").strip()
        contact = request.POST.get("txt_contact", "").strip()
        address = request.POST.get("txt_address", "").strip()
        password = request.POST.get("txt_password", "").strip()
        programme_id = request.POST.get("sel_programme")
        batch_id = request.POST.get("sel_batch")
        photo = request.FILES.get("photo")

        # Validation for duplicates
        if tbl_student.objects.filter(student_email=email).exists():
            return render(request, 'Guest/StudentRegister.html', {
                'error': 'A student with this Email is already registered.',
                'programmes': programmes, 'batches': batches
            })
        if regno and tbl_student.objects.filter(student_regno=regno).exists():
            return render(request, 'Guest/StudentRegister.html', {
                'error': 'A student with this Register Number is already registered.',
                'programmes': programmes, 'batches': batches
            })

        prog = tbl_programme.objects.get(id=programme_id)
        batch_obj = tbl_batch.objects.get(id=batch_id) if batch_id else None

        student_obj = tbl_student.objects.create(
            programme=prog,
            batch=batch_obj,
            student_regno=regno,
            student_name=name,
            student_gender=gender,
            student_dob=dob,
            student_email=email,
            student_contact=contact,
            student_address=address,
            student_password=password,
            student_photo=photo
        )

        create_notification('admin', 0, 'New Student Registration', f"Student {name} ({regno}) registered and requires verification.")

        return render(request, 'Guest/Login.html', {'msg': 'Student registration successful! Pending admin verification.'})

    return render(request, 'Guest/StudentRegister.html', {'programmes': programmes, 'batches': batches})

def CompanyRegister(request):
    if request.method == "POST":
        name = request.POST.get("txt_name", "").strip()
        email = request.POST.get("txt_email", "").strip()
        contact = request.POST.get("txt_contact", "").strip()
        address = request.POST.get("txt_address", "").strip()
        website = request.POST.get("txt_website", "").strip()
        industry = request.POST.get("txt_industry", "").strip()
        description = request.POST.get("txt_description", "").strip()
        password = request.POST.get("txt_password", "").strip()
        logo = request.FILES.get("logo")
        proof = request.FILES.get("proof")

        if tbl_company.objects.filter(company_email=email).exists():
            return render(request, 'Guest/CompanyRegister.html', {'error': 'A company with this email is already registered.'})

        company_obj = tbl_company.objects.create(
            company_name=name,
            company_email=email,
            company_contact=contact,
            company_address=address,
            company_website=website,
            company_industry=industry,
            company_description=description,
            company_password=password,
            company_logo=logo,
            company_proof=proof
        )

        create_notification('admin', 0, 'New Company Registration', f"Company {name} registered and requires verification.")

        return render(request, 'Guest/Login.html', {'msg': 'Company registration successful! Pending admin approval.'})

    return render(request, 'Guest/CompanyRegister.html')

def Logout(request):
    if 'name' in request.session:
        log_action(request.session.get('name', 'User'), 'User', 'Logout', 'Authentication')
    request.session.flush()
    return redirect('Guest:Login')

