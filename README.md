# EduTrack-X (50-60% Core Edition with Company Module)

**EduTrack-X Core Edition** is a streamlined, standalone Django web application developed for managing core student credit tracking, academic department master data, user registrations, corporate company opportunities, and faculty mentoring.

---

## 🗺️ Modules Overview (50-60% Core Scope)

This edition implements 5 core modules (~60% of the total full platform) free of bugs or errors:

### 1. ⚙️ Administrator Module (`/Administrator/`)
* **Dashboard:** Metrics overview of registered students, faculty guides, companies, departments, programmes, and pending approvals.
* **Department CRUD:** Create, edit, and delete academic departments.
* **Programme CRUD:** Register degree programmes (e.g. BCA, B.Tech) with total required credits and semester durations.
* **Academic Years & Batches:** Manage session years and student admission batches.
* **Account Approvals:** Review and approve/reject pending Student, Faculty, and Company user registrations.
* **Assign Faculty Mentees:** Assign faculty guides to registered students.
* **System Reports:** Detailed summary rosters of students, faculty, companies, and academic programmes.

### 2. 🏢 Company Module (`/Company/`)
* **Dashboard:** Overview of active posted vacancies, total applications, and selected candidates.
* **Post Opportunity:** Post corporate internship opportunities with duration, required skills, stipend, and last dates.
* **My Vacancies:** List, edit, or delete posted opportunities.
* **Applications Desk:** Review student applicants and update candidate selection statuses (Accept / Reject).
* **Profile Management:** View, edit company profile details (website, industry, logo, proof document), and change account passwords.

### 3. 🎓 Student Module (`/Student/`)
* **Dashboard:** Displays degree programme details, assigned faculty mentor, total earned credits, credit transaction ledger, and application status.
* **Browse Internships:** Explore verified company vacancies with search filtering.
* **Company Profile:** View details and active openings of corporate partners.
* **Apply for Internships:** Apply for posted vacancies and track selection results.
* **Credit Ledger:** View detailed credit awards (Seminar, Certification, Projects, etc.).
* **Profile Management:** View, edit personal profile details, and update account passwords.

### 4. 🧑‍🏫 Faculty Module (`/Faculty/`)
* **Dashboard:** Overview of assigned student mentees and department metrics.
* **Assigned Mentees:** View student rosters assigned to the faculty.
* **Student Monitor:** Inspect individual student academic profiles and earned credit history.
* **Profile Management:** View, edit personal profile details, and update account passwords.

### 5. 🌐 Guest Module (`/`)
* **Index Page:** Modern landing page with portal overview.
* **Student Registration:** Public signup form with programme, batch selection, and document upload.
* **Company Registration:** Public signup form with logo and verification proof document upload.
* **Login & Logout:** Role-based authentication gateway handling automatic session routing to Admin, Company, Faculty, or Student dashboards. (Faculty accounts are added directly by Admin).

---

## 🗄️ Database Tables (`tbl_*`)

This edition utilizes 10 normalized database models:

1. **`tbl_adminregistration`**: Admin credentials (`name`, `email`, `contact`, `password`).
2. **`tbl_department`**: Academic department records (`department_name`).
3. **`tbl_programme`**: Degree programme records (`programme_name`, `programme_duration`, `programme_totalcredit`, `department`).
4. **`tbl_batch`**: Admission cohorts (`batch_name`).
5. **`tbl_academicyear`**: Session years (`academicyear_name`).
6. **`tbl_student`**: Student account data (`student_regno`, `student_name`, `student_gender`, `student_dob`, `student_email`, `student_contact`, `student_address`, `student_photo`, `student_password`, `student_status`, `programme`, `batch`, `assigned_faculty`).
7. **`tbl_faculty`**: Faculty guide account data (`faculty_name`, `faculty_email`, `faculty_contact`, `faculty_address`, `faculty_photo`, `faculty_password`, `faculty_status`, `department`).
8. **`tbl_company`**: Company account data (`company_name`, `company_email`, `company_contact`, `company_address`, `company_website`, `company_industry`, `company_description`, `company_logo`, `company_proof`, `company_password`, `company_status`).
9. **`tbl_opportunity`**: Corporate vacancies (`company`, `opportunity_title`, `opportunity_description`, `skills_required`, `duration`, `stipend`, `last_date`, `posted_date`).
10. **`tbl_internship`**: Student applications (`opportunity`, `company`, `student`, `faculty`, `applied_date`, `internship_status`).
11. **`tbl_studentcredit`**: Academic credit ledger (`student`, `credit_type`, `credit_value`, `credit_remark`, `credit_date`).

---

## 🔑 Default Login Credentials (Pre-seeded)

The database `db.sqlite3` comes pre-populated with ready-to-use accounts for immediate testing:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@gmail.com` | `admin123` | Full system control & account approvals |
| **Company** | `company@gmail.com` | `company123` | TechCorp Solutions (Post vacancies & select interns) |
| **Faculty Guide** | `faculty@gmail.com` | `faculty123` | Dr. Robert Vance (CS Dept) |
| **Student** | `student@gmail.com` | `student123` | Alex Mercer (BCA 2024-2027) |

---

## 💻 How to Run the Project

1. **Navigate to project directory:**
   ```bash
   cd d:\Jithin\EduTrack_X_Completed\EduTrackX_50Percent
   ```

2. **Apply migrations & seed data (optional, database already initialized):**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python seed_data.py
   ```

3. **Run development server:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

4. Open your browser and go to `http://127.0.0.1:8000/` to test!
