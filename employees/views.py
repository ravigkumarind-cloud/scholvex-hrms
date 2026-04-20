from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime
import os


# =============================
# EMPLOYEE LIST
# =============================

@login_required
def employee_list(request):

    employees = Employee.objects.all()

    return render(request,'employees.html',{'employees':employees})


# =============================
# ADD EMPLOYEE
# =============================

from django.contrib.auth.models import User

@login_required
def add_employee(request):

    departments = Department.objects.all()

    if request.method == "POST":

        username = request.POST['email']
        password = "123456"

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Employee.objects.create(
            user=user,
            name=request.POST['name'],
            email=request.POST['email'],
            department_id=request.POST['department'],
            designation=request.POST['designation'],
            salary=request.POST['salary'],
            joining_date=request.POST['joining_date']
        )

        return redirect('employees')

    return render(request,'add_employee.html',{'departments':departments})


# =============================
# EDIT EMPLOYEE
# =============================

@login_required
def edit_employee(request,id):

    employee = Employee.objects.get(id=id)
    departments = Department.objects.all()

    if request.method == "POST":

        employee.name = request.POST['name']
        employee.email = request.POST['email']
        employee.department_id = request.POST['department']
        employee.designation = request.POST['designation']
        employee.salary = request.POST['salary']
        employee.joining_date = request.POST['joining_date']

        employee.save()

        return redirect('employees')

    return render(request,'edit_employee.html',{
        'employee':employee,
        'departments':departments
    })


# =============================
# DELETE EMPLOYEE
# =============================

@login_required
def delete_employee(request,id):

    Employee.objects.get(id=id).delete()

    return redirect('employees')


# =============================
# EMPLOYEE DASHBOARD
# =============================

@login_required
def employee_dashboard(request):

    employee = Employee.objects.get(user=request.user)

    return render(request,'employee_dashboard.html',{'employee':employee})


# =============================
# MARK ATTENDANCE
# =============================

@login_required
def mark_attendance(request):

    employee = Employee.objects.get(user=request.user)

    today = datetime.date.today()

    exists = Attendance.objects.filter(
        employee=employee,
        date=today
    ).exists()

    if not exists:

        Attendance.objects.create(
            employee=employee,
            date=today
        )

    return render(request,'attendance.html')


# =============================
# ATTENDANCE REPORT
# =============================

@login_required
def attendance_report(request):

    attendance = Attendance.objects.all()

    return render(request,'attendance_report.html',{
        'attendance':attendance
    })


# =============================
# APPLY LEAVE
# =============================

@login_required
def apply_leave(request):

    employee = Employee.objects.get(user=request.user)

    if request.method == "POST":

        Leave.objects.create(
            employee=employee,
            reason=request.POST['reason'],
            from_date=request.POST['from_date'],
            to_date=request.POST['to_date']
        )

        return redirect('employee_dashboard')

    return render(request,'apply_leave.html')


# =============================
# LEAVE LIST
# =============================

@login_required
def leave_list(request):

    leaves = Leave.objects.all()

    return render(request,'leave_list.html',{
        'leaves':leaves
    })


# =============================
# ADD PAYROLL
# =============================

@login_required
def add_payroll(request):

    employees = Employee.objects.all()

    if request.method == "POST":

        emp_id = request.POST['employee']
        basic = int(request.POST['basic'])
        bonus = int(request.POST['bonus'])

        employee = Employee.objects.get(id=emp_id)

        present = Attendance.objects.filter(
            employee=employee
        ).count()

        total_days = 30

        per_day = basic / total_days

        salary = int(per_day * present)

        hra = int(salary * 0.20)
        pf = int(salary * 0.12)

        net = salary + hra + bonus - pf

        Payroll.objects.create(
            employee=employee,
            month=request.POST['month'],
            basic=salary,
            hra=hra,
            pf=pf,
            bonus=bonus,
            net_salary=net
        )

        return redirect('payroll')

    return render(request,'add_payroll.html',{'employees':employees})


# =============================
# PAYROLL LIST
# =============================

@login_required
def payroll_list(request):

    payroll = Payroll.objects.all()

    return render(request,'payroll_list.html',{
        'payroll':payroll
    })


# =============================
# MY SALARY
# =============================

@login_required
def my_salary(request):

    employee = Employee.objects.get(user=request.user)

    salary = Payroll.objects.filter(employee=employee)

    return render(request,'my_salary.html',{
        'salary':salary
    })


# =============================
# PAYSLIP PDF
# =============================

@login_required
def payslip_pdf(request,id):

    payroll = Payroll.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Payslip.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    # company
    p.setFont("Helvetica-Bold",16)
    p.drawString(200,800,"SCHOLVEX SOLUTIONS")

    p.setFont("Helvetica",10)
    p.drawString(230,780,"Salary Payslip")

    p.drawString(50,740,f"Employee : {payroll.employee.name}")
    p.drawString(50,720,f"Month : {payroll.month}")
    p.drawString(50,700,f"Department : {payroll.employee.department}")
    p.drawString(50,680,f"Designation : {payroll.employee.designation}")

    p.line(50,660,500,660)

    p.drawString(50,630,"Basic")
    p.drawString(300,630,str(payroll.basic))

    p.drawString(50,610,"HRA")
    p.drawString(300,610,str(payroll.hra))

    p.drawString(50,590,"Bonus")
    p.drawString(300,590,str(payroll.bonus))

    p.drawString(50,570,"PF")
    p.drawString(300,570,str(payroll.pf))

    p.line(50,550,500,550)

    p.setFont("Helvetica-Bold",12)

    p.drawString(50,520,"Net Salary")
    p.drawString(300,520,str(payroll.net_salary))

    p.save()

    return response

from django.contrib.auth import update_session_auth_hash

@login_required
def change_password(request):

    if request.method == "POST":

        new_password = request.POST['password']

        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return redirect('employee_dashboard')

    return render(request,'change_password.html')

@login_required
def edit_profile(request):

    employee = Employee.objects.get(user=request.user)

    if request.method == "POST":

        employee.name = request.POST['name']
        employee.email = request.POST['email']
        employee.designation = request.POST['designation']

        if request.FILES.get('photo'):
            employee.photo = request.FILES['photo']

        employee.save()

        return redirect('employee_dashboard')

    return render(request,'edit_profile.html',{'employee':employee})

def add_employee(request):

    if request.method == "POST":

        name = request.POST['name']
        email = request.POST['email']
        department = request.POST['department']
        designation = request.POST['designation']
        role = request.POST['role']

        Employee.objects.create(
            name=name,
            email=email,
            department=department,
            designation=designation,
            role=role
        )

        return redirect('employees')

    return render(request,'add_employee.html')

from .models import Employee

def add_employee(request):

    managers = Employee.objects.all()

    if request.method == "POST":

        name = request.POST['name']
        email = request.POST['email']
        department = request.POST['department']
        designation = request.POST['designation']
        role = request.POST['role']
        reporting_to = request.POST.get('reporting_to')

        manager = None
        if reporting_to:
            manager = Employee.objects.get(id=reporting_to)

        Employee.objects.create(
            name=name,
            email=email,
            department=department,
            designation=designation,
            role=role,
            reporting_to=manager
        )

        return redirect('employees')

    return render(request,'add_employee.html',{'managers':managers})

from .models import Employee

def hierarchy(request):

    employees = Employee.objects.filter(reporting_to=None)

    return render(
        request,
        'employees/hierarchy.html',
        {'employees': employees}
    )
from django.shortcuts import render
from .models import Employee

def hierarchy(request):
    employees = Employee.objects.select_related('reporting_to').all()
    return render(request, 'employees/hierarchy.html', {'employees': employees})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee

@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            # 🔥 FORM DATA (Flutter nundi vastundi)
            username = request.POST.get("username")
            password = request.POST.get("password")

            print("USERNAME:", username)
            print("PASSWORD:", password)

            # 🔥 SIMPLE LOGIN (email based)
            user = Employee.objects.filter(email=username).first()

            if user:
                return JsonResponse({
                    "status": "success",
                    "role": user.role
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "User not found"
                })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({"status": "error"})


@csrf_exempt
def add_employee_api(request):
    if request.method == "POST":
        try:
            # 🔍 DEBUG PRINT (ADD HERE)
            print("DATA:", request.POST)

            name = request.POST.get("name")
            email = request.POST.get("email")
            department = request.POST.get("department")
            designation = request.POST.get("designation")
            salary = request.POST.get("salary")

            # 🔥 IMPORTANT FIX (salary int conversion)
            emp = Employee.objects.create(
                name=name,
                email=email,
                department=department,
                designation=designation,
                salary=int(salary) if salary else 0
            )

            return JsonResponse({
                "status": "success",
                "message": "Employee added"
            })

        except Exception as e:
            print("ERROR:", e)   # 🔍 DEBUG
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({"status": "error"})

@csrf_exempt
def update_employee_api(request, id):
    if request.method == "POST":
        try:
            emp = Employee.objects.get(id=id)

            emp.name = request.POST.get("name")
            emp.email = request.POST.get("email")
            emp.department = request.POST.get("department")
            emp.designation = request.POST.get("designation")
            emp.salary = request.POST.get("salary")

            emp.save()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error"})


@csrf_exempt
def delete_employee_api(request, id):
    if request.method == "POST":
        try:
            emp = Employee.objects.get(id=id)
            emp.delete()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error"})


def employee_list_api(request):
    employees = Employee.objects.all().values()

    return JsonResponse({
        "status": "success",
        "data": list(employees)
    })