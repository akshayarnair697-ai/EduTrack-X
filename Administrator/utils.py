from django.db.models import Sum, Q
from Administrator.models import (
    tbl_activitycategory, tbl_creditrequirement, tbl_notification, tbl_auditlog
)
from Guest.models import tbl_student
from Student.models import tbl_studentcredit, tbl_studentactivity, tbl_certificate
from Company.models import tbl_internship, tbl_internshipreport

def create_notification(recipient_role, recipient_id, title, message, url=""):
    """
    Creates a notification entry in tbl_notification.
    recipient_role: 'student', 'faculty', 'company', 'admin'
    recipient_id: ID of user (or 0 for admin/global)
    """
    try:
        tbl_notification.objects.create(
            recipient_role=recipient_role,
            recipient_id=recipient_id,
            title=title,
            message=message,
            related_url=url
        )
    except Exception as e:
        print(f"Error creating notification: {e}")

def log_action(user_name, user_role, action, related_module, related_id=None, description=""):
    pass

def get_student_credit_summary(student_id):
    """
    Computes complete dynamic credit metrics and completion status for a student.
    Returns a dictionary with comprehensive breakdown.
    """
    try:
        student = tbl_student.objects.get(id=student_id)
    except tbl_student.DoesNotExist:
        return None

    programme = student.programme

    # Fetch total programme credit target
    total_prog_required = programme.programme_totalcredit if programme else 0

    # Fetch configured credit requirements
    requirements = tbl_creditrequirement.objects.filter(programme=programme)
    req_dict = {}
    for r in requirements:
        req_dict[r.activity_category.id] = {
            'category_name': r.activity_category.category_name,
            'required': r.required_credit
        }

    # Fetch all active categories
    categories = tbl_activitycategory.objects.filter(status=1)
    
    # Approved credits
    approved_credits = tbl_studentcredit.objects.filter(student=student, approval_status=1)
    total_earned = sum(c.credit_value for c in approved_credits)

    # Pending credits (under review)
    pending_credits = tbl_studentcredit.objects.filter(student=student, approval_status=0)
    total_pending = sum(c.credit_value for c in pending_credits)

    # Category-wise breakdown
    category_summary = []
    total_req_from_categories = 0

    for cat in categories:
        cat_req = req_dict.get(cat.id, {}).get('required', cat.default_credit or 0)
        total_req_from_categories += cat_req

        # Filter credits matching category or fallback source matching category name
        cat_approved = approved_credits.filter(
            Q(credit_category=cat) | Q(credit_type__icontains=cat.category_name) | Q(source_type__icontains=cat.category_name)
        )
        earned = sum(c.credit_value for c in cat_approved)
        
        cat_pending_objs = pending_credits.filter(
            Q(credit_category=cat) | Q(credit_type__icontains=cat.category_name) | Q(source_type__icontains=cat.category_name)
        )
        pending = sum(c.credit_value for c in cat_pending_objs)

        remaining = max(0, cat_req - earned)
        status_label = "Completed" if earned >= cat_req and cat_req > 0 else ("In Progress" if earned > 0 else "Pending")

        category_summary.append({
            'category_id': cat.id,
            'category_name': cat.category_name,
            'required': cat_req,
            'earned': earned,
            'pending': pending,
            'remaining': remaining,
            'percentage': round((earned / cat_req) * 100) if cat_req > 0 else (100 if earned > 0 else 0),
            'status': status_label
        })

    # Effective total required
    target_required = max(total_prog_required, total_req_from_categories)
    total_remaining = max(0, target_required - total_earned)
    completion_percentage = round((total_earned / target_required) * 100) if target_required > 0 else 0
    if completion_percentage > 100:
        completion_percentage = 100

    # Semester-wise summary
    semester_summary = []
    for sem in range(1, 9):
        sem_credits = approved_credits.filter(semester=sem)
        sem_earned = sum(c.credit_value for c in sem_credits)
        if sem_earned > 0 or sem <= (programme.programme_duration * 2 if programme else 6):
            semester_summary.append({
                'semester': sem,
                'earned': sem_earned,
                'count': sem_credits.count()
            })

    # Check internships & certificates
    internships = tbl_internship.objects.filter(student=student)
    completed_internship = internships.filter(internship_status=7).exists() # 7: Completed
    ongoing_internship = internships.filter(internship_status__in=[2, 3, 4, 5, 6]).first()

    certificates = tbl_certificate.objects.filter(student=student)
    approved_certs_count = certificates.filter(status=1).count()
    pending_certs_count = certificates.filter(status=0).count()

    activities = tbl_studentactivity.objects.filter(student=student)
    completed_activities_count = activities.filter(status__in=[4, 6]).count()

    # Missing requirements list generator
    missing_requirements = []
    for cat in category_summary:
        if cat['remaining'] > 0:
            missing_requirements.append(f"{cat['remaining']} {cat['category_name']} Credits")

    if not completed_internship:
        if ongoing_internship:
            missing_requirements.append("Internship Final Evaluation & Approval Pending")
        else:
            missing_requirements.append("Internship Completion Required")

    # Eligibility Checker logic
    all_categories_met = all(cat['earned'] >= cat['required'] for cat in category_summary if cat['required'] > 0)
    total_credits_met = total_earned >= target_required

    if total_earned == 0 and completed_activities_count == 0:
        eligibility_status = "Not Started"
        eligibility_class = "badge-danger"
    elif total_credits_met and all_categories_met and completed_internship:
        eligibility_status = "Eligible for Programme Completion"
        eligibility_class = "badge-success"
    else:
        eligibility_status = "Requirements Pending"
        eligibility_class = "badge-pending"

    return {
        'student': student,
        'target_required': target_required,
        'total_earned': total_earned,
        'total_pending': total_pending,
        'total_remaining': total_remaining,
        'completion_percentage': completion_percentage,
        'category_summary': category_summary,
        'semester_summary': semester_summary,
        'approved_credits_list': approved_credits.order_by('-credit_date'),
        'missing_requirements': missing_requirements,
        'eligibility_status': eligibility_status,
        'eligibility_class': eligibility_class,
        'completed_internship': completed_internship,
        'approved_certs_count': approved_certs_count,
        'pending_certs_count': pending_certs_count,
        'completed_activities_count': completed_activities_count,
    }
