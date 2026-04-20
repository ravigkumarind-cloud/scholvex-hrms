from django.urls import path
from . import views

urlpatterns = [

    # 🔥 API ROUTES
    path('login/', views.api_login),
    path('employees/', views.employee_list_api), 
    path('add-employee/', views.add_employee_api),
    path('update-employee/<int:id>/', views.update_employee_api),
    path('delete-employee/<int:id>/', views.delete_employee_api),

    # 🔽 WEB ROUTES (website kosam)
    path('', views.employee_list, name='employees'),
    path('add/', views.add_employee, name='add_employee'),
    path('edit/<int:id>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:id>/', views.delete_employee, name='delete_employee'),

    path('my-profile/', views.employee_dashboard, name='employee_dashboard'),

    path('attendance/', views.mark_attendance, name='attendance'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),

    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('leaves/', views.leave_list, name='leave_list'),

    path('payroll/', views.payroll_list, name='payroll'),
    path('my-salary/', views.my_salary, name='my_salary'),

    path('payslip/<int:id>/', views.payslip_pdf, name='payslip_pdf'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('hierarchy/', views.hierarchy, name='hierarchy'),
]