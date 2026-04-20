from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from employees.models import (
    Attendance, Employee, Leave, Payroll, DailyUpdate, Notification,
    Lead, Task, Commission
)
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required

# ===============================
# WEBSITE PAGES
# ===============================

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request,'company/about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')


# ===============================
# MAIN DASHBOARD
# ===============================

def dashboard(request):

    total_employees = Employee.objects.count()
    today = date.today()

    present = Attendance.objects.filter(date=today).count()
    absent = total_employees - present
    pending_leaves = Leave.objects.filter(status="Pending").count()
    total_salary = Payroll.objects.count()

    context = {
        "total_employees": total_employees,
        "present": present,
        "absent": absent,
        "pending_leaves": pending_leaves,
        "total_salary": total_salary
    }

    return render(request, "dashboard.html", context)


# ===============================
# CHAIRMAN
# ===============================

def chairman_dashboard(request):

    context = {
        'total_employees': Employee.objects.count(),
        'present': Attendance.objects.filter(status='Present').count(),
        'leaves': Leave.objects.filter(status='Pending').count(),
        'payroll': Payroll.objects.count(),
        'partners': 5,
        'branches': 3,
        'departments': 8
    }

    return render(request,'chairman/dashboard.html',context)


# ===============================
# MD
# ===============================

def md_dashboard(request):

    context = {
        'employees': Employee.objects.count(),
        'departments': 8,
        'present': Attendance.objects.filter(status='Present').count(),
        'leaves': Leave.objects.filter(status='Pending').count(),
        'payroll': 250000,
    }

    return render(request,'md/dashboard.html',context)


# ===============================
# DIRECTOR
# ===============================

def director_dashboard(request):

    context = {
        'employees': Employee.objects.count(),
        'present': Attendance.objects.filter(status='Present').count(),
        'leaves': Leave.objects.filter(status='Pending').count(),
    }

    return render(request,'director/dashboard.html',context)


# ===============================
# HOD
# ===============================

def hod_dashboard(request):

    context = {
        'employees': Employee.objects.count(),
        'present': Attendance.objects.filter(status='Present').count(),
        'leaves': Leave.objects.filter(status='Pending').count(),
    }

    return render(request,'hod/dashboard.html',context)


# ===============================
# MANAGER
# ===============================

def manager_dashboard(request):

    context = {
        'employees': Employee.objects.count(),
        'present': Attendance.objects.filter(status='Present').count(),
    }

    return render(request,'manager/dashboard.html',context)


def _department_workspace_context(request, department, title, metric_cards):
    employee = Employee.objects.filter(user=request.user).first()
    latest_payroll = Payroll.objects.filter(employee=employee).order_by('-created').first() if employee else None
    leave_history = Leave.objects.filter(employee=employee).order_by('-from_date')[:5] if employee else Leave.objects.none()
    notifications = StaffNotification.objects.filter(employee=employee) | StaffNotification.objects.filter(department__icontains=department)
    notifications = notifications.order_by('-created_at')[:6]

    return {
        'employee': employee,
        'department_title': title,
        'department_name': department,
        'metric_cards': metric_cards,
        'latest_payroll': latest_payroll,
        'leave_history': leave_history,
        'notifications': notifications,
    }


# ===============================
# MARKETING
# ===============================

@login_required
def marketing_dashboard(request):
    employee = Employee.objects.filter(user=request.user).first()
    today = date.today()

    if request.method == "POST" and employee:
        form_type = request.POST.get("form_type")

        if form_type == "daily_report":
            report_date = request.POST.get("date") or today
            MarketingDailyReport.objects.update_or_create(
                employee=employee,
                date=report_date,
                defaults={
                    "daily_target": int(request.POST.get("daily_target") or 0),
                    "closed_target": int(request.POST.get("closed_target") or 0),
                    "generated_leads": int(request.POST.get("generated_leads") or 0),
                    "followups": int(request.POST.get("followups") or 0),
                    "notes": request.POST.get("notes", ""),
                }
            )
            messages.success(request, "Daily marketing report saved.")
            return redirect("marketing_dashboard")

        if form_type == "leave":
            Leave.objects.create(
                employee=employee,
                reason=request.POST.get("reason", ""),
                from_date=request.POST.get("from_date"),
                to_date=request.POST.get("to_date"),
            )
            messages.success(request, "Leave request submitted.")
            return redirect("marketing_dashboard")

    team = Employee.objects.filter(department__icontains='marketing')
    reports = MarketingDailyReport.objects.filter(employee__in=team)
    my_reports = MarketingDailyReport.objects.filter(employee=employee) if employee else MarketingDailyReport.objects.none()
    recent_reports = my_reports.order_by('-date')[:7]
    latest_payroll = Payroll.objects.filter(employee=employee).order_by('-created').first() if employee else None
    payroll_history = Payroll.objects.filter(employee=employee).order_by('-created')[:6] if employee else Payroll.objects.none()
    leave_history = Leave.objects.filter(employee=employee).order_by('-from_date')[:5] if employee else Leave.objects.none()
    notifications = StaffNotification.objects.filter(employee=employee) | StaffNotification.objects.filter(department__icontains='marketing')
    notifications = notifications.order_by('-created_at')[:6]
    totals = reports.aggregate(
        total_leads=Sum('generated_leads'),
        total_followups=Sum('followups'),
        total_closed=Sum('closed_target'),
        total_target=Sum('daily_target'),
    )

    labels = []
    targets = []
    closed = []
    leads = []
    followups = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        report = my_reports.filter(date=day).first()
        labels.append(day.strftime("%d %b"))
        targets.append(report.daily_target if report else 0)
        closed.append(report.closed_target if report else 0)
        leads.append(report.generated_leads if report else 0)
        followups.append(report.followups if report else 0)

    total_target = sum(targets)
    total_closed = sum(closed)
    performance = int((total_closed / total_target) * 100) if total_target else 0

    context = {
        'employee': employee,
        'employees': team.count(),
        'today': today,
        'today_report': my_reports.filter(date=today).first(),
        'latest_payroll': latest_payroll,
        'payroll_history': payroll_history,
        'leave_history': leave_history,
        'notifications': notifications,
        'recent_reports': recent_reports,
        'campaigns': reports.count(),
        'leads': totals['total_leads'] or 0,
        'followups': totals['total_followups'] or 0,
        'conversions': totals['total_closed'] or 0,
        'targets': totals['total_target'] or 0,
        'pending': max(total_target - total_closed, 0),
        'performance': performance,
        'chart_labels': labels,
        'chart_targets': targets,
        'chart_closed': closed,
        'chart_leads': leads,
        'chart_followups': followups,
    }

    return render(request,'marketing/dashboard.html',context)


# ===============================
# SALES
# ===============================

@login_required
def sales_dashboard(request):

    context = _department_workspace_context(request, 'sales', 'Sales Department Dashboard', [
        {'label': 'Sales Team', 'value': Employee.objects.filter(department__icontains='sales').count()},
        {'label': 'Active Leads', 'value': 0},
        {'label': 'Closed Deals', 'value': 0},
        {'label': 'Revenue', 'value': 0},
    ])

    return render(request,'staff/department_dashboard.html',context)


# ===============================
# TL
# ===============================

def tl_dashboard(request):
    return render(request,'tl/dashboard.html')


# ===============================
# HR
# ===============================

@login_required
def hr_dashboard(request):
    context = _department_workspace_context(request, 'hr', 'HR Department Dashboard', [
        {'label': 'Employees', 'value': Employee.objects.count()},
        {'label': 'Leave Requests', 'value': Leave.objects.filter(status='Pending').count()},
        {'label': 'Present Today', 'value': Attendance.objects.filter(status='Present').count()},
        {'label': 'Payroll Records', 'value': Payroll.objects.count()},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# ACCOUNTS
# ===============================

@login_required
def accounts_dashboard(request):
    context = _department_workspace_context(request, 'accounts', 'Accounts Department Dashboard', [
        {'label': 'Accounts Team', 'value': Employee.objects.filter(department__icontains='accounts').count()},
        {'label': 'Payroll Records', 'value': Payroll.objects.count()},
        {'label': 'Pending Leaves', 'value': Leave.objects.filter(status='Pending').count()},
        {'label': 'Salary Slips', 'value': Payroll.objects.count()},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# PARTNER
# ===============================

def partner_dashboard(request):
    return render(request,'partner/dashboard.html')


# ===============================
# SECURITY
# ===============================

@login_required
def security_dashboard(request):
    context = _department_workspace_context(request, 'security', 'Security Department Dashboard', [
        {'label': 'Security Team', 'value': Employee.objects.filter(department__icontains='security').count()},
        {'label': 'Present Today', 'value': Attendance.objects.filter(status='Present').count()},
        {'label': 'Alerts', 'value': 0},
        {'label': 'Open Tasks', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# TECHNICAL
# ===============================

@login_required
def technical_dashboard(request):
    context = _department_workspace_context(request, 'technical', 'Technical Department Dashboard', [
        {'label': 'Technical Team', 'value': Employee.objects.filter(department__icontains='technical').count()},
        {'label': 'Support Tickets', 'value': 0},
        {'label': 'Deployments', 'value': 0},
        {'label': 'Pending Tasks', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# LEGAL
# ===============================

@login_required
def legal_dashboard(request):
    context = _department_workspace_context(request, 'legal', 'Legal Department Dashboard', [
        {'label': 'Legal Team', 'value': Employee.objects.filter(department__icontains='legal').count()},
        {'label': 'Agreements', 'value': 0},
        {'label': 'Pending Approvals', 'value': 0},
        {'label': 'Notices', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# BPO
# ===============================

@login_required
def bpo_dashboard(request):
    context = _department_workspace_context(request, 'bpo', 'BPO Department Dashboard', [
        {'label': 'BPO Team', 'value': Employee.objects.filter(department__icontains='bpo').count()},
        {'label': 'Calls Today', 'value': 0},
        {'label': 'Follow Ups', 'value': 0},
        {'label': 'Resolved', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# PRODUCTION
# ===============================

@login_required
def production_dashboard(request):
    context = _department_workspace_context(request, 'production', 'Production Department Dashboard', [
        {'label': 'Production Team', 'value': Employee.objects.filter(department__icontains='production').count()},
        {'label': 'Active Work', 'value': 0},
        {'label': 'Completed', 'value': 0},
        {'label': 'Pending', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# PRO
# ===============================

@login_required
def pro_dashboard(request):
    context = _department_workspace_context(request, 'pro', 'PRO Department Dashboard', [
        {'label': 'PRO Team', 'value': Employee.objects.filter(department__icontains='pro').count()},
        {'label': 'Visits', 'value': 0},
        {'label': 'Meetings', 'value': 0},
        {'label': 'Follow Ups', 'value': 0},
    ])
    return render(request,'staff/department_dashboard.html',context)


# ===============================
# ADMIN
# ===============================

def admin_dashboard(request):
    return render(request,'admin/dashboard.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("username")
            password = data.get("password")

            if username == "admin" and password == "1234":
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error"})
        except:
            return JsonResponse({"status": "error"})

    return JsonResponse({"status": "invalid"})