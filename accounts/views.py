import os
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from employees.models import Employee

from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from openai import OpenAI
from .models import CandidateProfile, ContactEnquiry, JobApplication, SupportTicket

# ==============================
# MAIN LOGIN (ROLE BASED)
# ==============================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)
            return _redirect_staff_user(user)

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def _redirect_staff_user(user):
    try:
        employee = Employee.objects.get(user=user)
        role = employee.role
        department = (employee.department or "").strip().upper()
    except Employee.DoesNotExist:
        if user.is_staff or user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('employee_dashboard')

    if role == "CHAIRMAN":
        return redirect('chairman_dashboard')
    if role == "MD":
        return redirect('md_dashboard')
    if role == "DIRECTOR":
        return redirect('director_dashboard')
    if role == "HOD":
        return redirect('hod_dashboard')
    if role == "MANAGER":
        return redirect('manager_dashboard')
    if role == "TL":
        return redirect('tl_dashboard')
    if role == "HR":
        return redirect('hr_dashboard')
    if role == "ACCOUNTS":
        return redirect('accounts_dashboard')
    if role == "TECHNICAL":
        return redirect('technical_dashboard')
    if role == "MARKETING":
        return redirect('marketing_dashboard')
    if role == "SALES":
        return redirect('sales_dashboard')
    if role == "BPO":
        return redirect('bpo_dashboard')
    if role == "PRO":
        return redirect('pro_dashboard')
    if role == "PRODUCTION":
        return redirect('production_dashboard')
    if role == "SECURITY":
        return redirect('security_dashboard')
    if role == "LEGAL":
        return redirect('legal_dashboard')

    if "HR" in department:
        return redirect('hr_dashboard')
    if "MARKETING" in department:
        return redirect('marketing_dashboard')
    if "SALES" in department:
        return redirect('sales_dashboard')
    if "TECHNICAL" in department:
        return redirect('technical_dashboard')
    if "ACCOUNTS" in department:
        return redirect('accounts_dashboard')
    if "LEGAL" in department:
        return redirect('legal_dashboard')
    if "BPO" in department:
        return redirect('bpo_dashboard')
    if "PRODUCTION" in department:
        return redirect('production_dashboard')
    if department == "PRO" or "PUBLIC RELATION" in department:
        return redirect('pro_dashboard')
    if "SECURITY" in department:
        return redirect('security_dashboard')
    if "MANAGEMENT" in department:
        return redirect('manager_dashboard')
    return redirect('employee_dashboard')


# ==============================
# LOGOUT
# ==============================

def logout_view(request):
    logout(request)
    return redirect('login')


# ==============================
# STAFF LOGIN PAGE
# ==============================

def staff_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None and (hasattr(user, "employee") or user.is_staff or user.is_superuser):
            login(request, user)
            return _redirect_staff_user(user)

        messages.error(request, "Invalid staff login details.")

    return render(request, "accounts/staff_login.html")


# ==============================
# PARTNER LOGIN
# ==============================

def partner_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('partner_dashboard')

        else:
            return render(request, 'accounts/partner_login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, "accounts/partner_login.html")


# ==============================
# PARTNER DASHBOARD
# ==============================

def partner_dashboard(request):
    return render(request, 'partner/dashboard.html')


# ==============================
# PARTNER PAGES
# ==============================

def partner_leads(request):
    return render(request, 'partner/leads.html')


def partner_customers(request):
    return render(request, 'partner/customers.html')


def partner_commission(request):
    return render(request, 'partner/commission.html')


def partner_reports(request):
    return render(request, 'partner/reports.html')


def partner_profile(request):
    return render(request, 'partner/profile.html')


def client_login(request):
    return render(request, 'accounts/client_login.html')

def candidate_login(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "candidate_dashboard"

    if request.user.is_authenticated and hasattr(request.user, "candidate_profile"):
        return redirect(next_url)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None and hasattr(user, "candidate_profile"):
            login(request, user)
            return redirect(next_url)

        messages.error(request, "Invalid candidate login details.")

    return render(request, 'accounts/candidate_login.html', {"next": next_url})


def candidate_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, "candidate_profile"):
        return redirect("/accounts/login/candidate/?next=/accounts/candidate/dashboard/")

    applications = JobApplication.objects.filter(candidate=request.user)
    return render(request, "accounts/candidate_dashboard.html", {
        "profile": request.user.candidate_profile,
        "applications": applications,
    })


def candidate_apply(request):
    job_title = request.GET.get("job", "Open Position")
    department = request.GET.get("department", "Careers")
    location = request.GET.get("location", "Hyderabad")

    if not request.user.is_authenticated or not hasattr(request.user, "candidate_profile"):
        return redirect(f"/accounts/login/candidate/?next={quote(request.get_full_path())}")

    existing = JobApplication.objects.filter(candidate=request.user, job_title=job_title).first()

    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter", "")
        resume = request.FILES.get("resume")

        application, created = JobApplication.objects.get_or_create(
            candidate=request.user,
            job_title=job_title,
            defaults={
                "department": department,
                "location": location,
                "cover_letter": cover_letter,
                "resume": resume,
            },
        )

        if not created:
            application.department = department
            application.location = location
            application.cover_letter = cover_letter
            if resume:
                application.resume = resume
            application.save()

        messages.success(request, "Application submitted successfully.")
        return redirect("candidate_dashboard")

    return render(request, "accounts/candidate_apply.html", {
        "job_title": job_title,
        "department": department,
        "location": location,
        "existing": existing,
    })


def _can_manage_candidates(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    try:
        return Employee.objects.get(user=user).role in {"HR", "HOD", "MANAGER", "DIRECTOR", "MD", "CHAIRMAN"}
    except Employee.DoesNotExist:
        return False


def candidate_application_board(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/staff/")
    if not _can_manage_candidates(request.user):
        return HttpResponseForbidden("You do not have permission to manage candidate applications.")

    if request.method == "POST":
        application_id = request.POST.get("application_id")
        status = request.POST.get("status")
        notes = request.POST.get("notes", "")

        if status in dict(JobApplication.STATUS_CHOICES):
            JobApplication.objects.filter(id=application_id).update(status=status, notes=notes)
            messages.success(request, "Candidate application status updated.")

        return redirect("candidate_application_board")

    applications = JobApplication.objects.select_related("candidate", "candidate__candidate_profile")
    return render(request, "accounts/candidate_application_board.html", {
        "applications": applications,
        "status_choices": JobApplication.STATUS_CHOICES,
    })

# ==============================
# COMPANY PAGES
# ==============================

def about(request):
    return render(request,'company/about.html')

def vision(request):
    return render(request,'company/vision.html')

def leadership(request):
    return render(request,'company/leadership.html')

def clients(request):
    return render(request,'company/clients.html')

def partners(request):
    return render(request,'company/partners.html')

def careers(request):
    return render(request,'company/careers.html')

def company_profile(request):
    return render(request,'company/company_profile.html')

def presence(request):
    return render(request,'company/presence.html')

def strength(request):
    return render(request,'company/strength.html')

def terms(request):
    return render(request,'company/terms.html')

def privacy(request):
    return render(request,'company/privacy.html')

def disclaimer(request):
    return render(request,'company/disclaimer.html')




# =========================
# PRODUCTS
# =========================

def school_erp(request):
    return render(request,'products/school_erp.html')

def college_erp(request):
    return render(request,'products/college_erp.html')

def institute_erp(request):
    return render(request,'products/institute_erp.html')

def lms(request):
    return render(request,'products/lms.html')

def mobile_app(request):
    return render(request,'products/mobile_app.html')


# TECHNICAL

def biometric(request):
    return render(request,'products/biometric.html')

def cctv(request):
    return render(request,'products/cctv.html')

def rfid(request):
    return render(request,'products/rfid.html')

def smart_class(request):
    return render(request,'products/smart_class.html')

def solar(request):
    return render(request,'products/solar.html')

def gps(request):
    return render(request,'products/gps.html')


# COMMUNICATION

def bulk_sms(request):
    return render(request,'products/bulk_sms.html')

def rcs_sms(request):
    return render(request,'products/rcs_sms.html')

def whatsapp(request):
    return render(request,'products/whatsapp.html')

def voice_call(request):
    return render(request,'products/voice_call.html')

def email(request):
    return render(request,'products/email.html')

def notification(request):
    return render(request,'products/notification.html')


# SCHOOL ESSENTIALS

def id_cards(request):
    return render(request,'products/id_cards.html')

def uniforms(request):
    return render(request,'products/uniforms.html')

def tie_belt(request):
    return render(request,'products/tie_belt.html')

def bags(request):
    return render(request,'products/bags.html')

def notebooks(request):
    return render(request,'products/notebooks.html')

def diaries(request):
    return render(request,'products/diaries.html')


# PRINTING

def textbooks(request):
    return render(request,'products/textbooks.html')

def certificates(request):
    return render(request,'products/certificates.html')

def report_cards(request):
    return render(request,'products/report_cards.html')

def mementos(request):
    return render(request,'products/mementos.html')

def printing(request):
    return render(request,'products/printing.html')


# INFRASTRUCTURE

def furniture(request):
    return render(request,'products/furniture.html')

def lab_setup(request):
    return render(request,'products/lab_setup.html')

def smart_classroom(request):
    return render(request,'products/smart_classroom.html')

def computer_lab(request):
    return render(request,'products/computer_lab.html')



def school_solution(request):
    return render(request,'solutions/school.html')

def college_solution(request):
    return render(request,'solutions/college.html')

def institute_solution(request):
    return render(request,'solutions/institute.html')

def smart_campus(request):
    return render(request,'solutions/smart_campus.html')

def digital_communication(request):
    return render(request,'solutions/digital_communication.html')

def communication(request):
    return render(request,'solutions/communication.html')

def automation(request):
    return render(request,'solutions/automation.html')

def student_management(request):
    return render(request,'solutions/student_management.html')

def staff_management(request):
    return render(request,'solutions/staff_management.html')

def attendance(request):
    return render(request,'solutions/attendance.html')

def fee_management(request):
    return render(request,'solutions/fee_management.html')

# ================= SERVICES =================

def website_development(request):
    return render(request,'services/website_development.html')

def app_development(request):
    return render(request,'services/app_development.html')

def erp_setup(request):
    return render(request,'services/erp_setup.html')

def portal_development(request):
    return render(request,'services/portal_development.html')


# TECHNICAL SERVICES

def installation(request):
    return render(request,'services/installation.html')

def networking(request):
    return render(request,'services/networking.html')

def server_setup(request):
    return render(request,'services/server_setup.html')

def smart_class_setup(request):
    return render(request,'services/smart_class_setup.html')


# ADMISSION SUPPORT

def student_counselling(request):
    return render(request,'services/student_counselling.html')

def admission_campaign(request):
    return render(request,'services/admission_campaign.html')

def lead_generation(request):
    return render(request,'services/lead_generation.html')

def seat_filling(request):
    return render(request,'services/seat_filling.html')


# EVENT MANAGEMENT

def annual_day(request):
    return render(request,'services/annual_day.html')

def sports_day(request):
    return render(request,'services/sports_day.html')

def college_fest(request):
    return render(request,'services/college_fest.html')

def seminars(request):
    return render(request,'services/seminars.html')


# STAFFING

def teaching_staff(request):
    return render(request,'services/teaching_staff.html')

def non_teaching_staff(request):
    return render(request,'services/non_teaching_staff.html')

def admin_staff(request):
    return render(request,'services/admin_staff.html')

def marketing_staff(request):
    return render(request,'services/marketing_staff.html')


# DIGITAL MARKETING

def admission_marketing(request):
    return render(request,'services/admission_marketing.html')

def social_media(request):
    return render(request,'services/social_media.html')

def seo(request):
    return render(request,'services/seo.html')

def paid_ads(request):
    return render(request,'services/paid_ads.html')

def whatsapp_sms(request):
    return render(request,'services/whatsapp_sms.html')

def branding(request):
    return render(request,'services/branding.html')

def website_marketing(request):
    return render(request,'services/website_marketing.html')

def analytics(request):
    return render(request,'services/analytics.html')


# ACADEMIC

def tutors(request):
    return render(request,'services/tutors.html')

def guest_faculty(request):
    return render(request,'services/guest_faculty.html')

def trainers(request):
    return render(request,'services/trainers.html')

def coaching_faculty(request):
    return render(request,'services/coaching_faculty.html')


# MAINTENANCE

def electrician(request):
    return render(request,'services/electrician.html')

def plumbing(request):
    return render(request,'services/plumbing.html')

def painting(request):
    return render(request,'services/painting.html')

def renovations(request):
    return render(request,'services/renovations.html')

def amc(request):
    return render(request,'services/amc.html')


# MANAGEMENT

def school_management(request):
    return render(request,'management/school.html')

def college_management(request):
    return render(request,'management/college.html')

def institute_management(request):
    return render(request,'management/institute.html')


def hr_management(request):
    return render(request,'management/hr.html')

def accounts_management(request):
    return render(request,'management/accounts.html')

def admission_management(request):
    return render(request,'management/admissions.html')


def transport_management(request):
    return render(request,'management/transport.html')

def hostel_management(request):
    return render(request,'management/hostel.html')

def facility_management(request):
    return render(request,'management/facility.html')

def security_management(request):
    return render(request,'management/security.html')



def helpdesk(request):
    return render(request,'support/helpdesk.html')

def ticket_support(request):
    return render(request,'support/ticket-support.html')

def remote_support(request):
    return render(request,'support/remote-support.html')

def amc_plans(request):
    return render(request,'support/amc.html')

def preventive_maintenance(request):
    return render(request,'support/preventive.html')

def onsite_support(request):
    return render(request,'support/onsite.html')

def raise_ticket(request):
    return render(request,'support/raise-ticket.html')

def track_ticket(request):
    return render(request,'support/track-ticket.html')

def service_request(request):
    return render(request,'support/service-request.html')

def user_manuals(request):
    return render(request,'support/manuals.html')

def documentation(request):
    return render(request,'support/docs.html')

def software_downloads(request):
    return render(request,'support/downloads.html')




client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@csrf_exempt
def ai_chat(request):
    try:
        data = json.loads(request.body)
        user_message = data.get("message")

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are ScholVex AI assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({"reply": str(e)})
    

from .models import ContactEnquiry

def contact_submit(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')
        message = request.POST.get('message')

        ContactEnquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            organization=organization,
            message=message
        )

    return redirect('/contact/?success=1')

    return redirect('/contact/')



from .models import SupportTicket

def submit_ticket(request):

    if request.method == "POST":

        ticket = SupportTicket.objects.create(
            name=request.POST.get('name'),
            institution=request.POST.get('institution'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            product=request.POST.get('product'),
            priority=request.POST.get('priority'),
            message=request.POST.get('message')
        )

        return redirect(f"/support/raise-ticket/?success={ticket.ticket_id}")

    return redirect('/support/raise-ticket/')


from .models import SupportTicket

def track_ticket(request):

    ticket = None

    if request.method == "POST":
        ticket_id = request.POST.get('ticket_id')
        phone = request.POST.get('phone')

        try:
            ticket = SupportTicket.objects.get(ticket_id=ticket_id)
        except:
            ticket = None

    return render(request, 'support/track-ticket.html', {'ticket': ticket})


from django.shortcuts import render

def client_login(request):
    return render(request, 'accounts/client_login.html')


def client_signup(request):
    return render(request, 'accounts/client_signup.html')

def candidate_signup(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "candidate_dashboard"

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        qualification = request.POST.get("qualification", "").strip()
        skills = request.POST.get("skills", "").strip()
        password = request.POST.get("password", "")

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please login.")
            return redirect(f"/accounts/login/candidate/?next={quote(next_url)}")

        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        CandidateProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            qualification=qualification,
            skills=skills,
        )
        login(request, user)
        return redirect(next_url)

    return render(request, 'accounts/candidate_signup.html', {"next": next_url})


def forgot_password(request):
    return render(request, 'accounts/forgot_password.html')
