from django.contrib import admin
from .models import (
    Department, Role, Employee, Lead, Task, Partner, DailyUpdate,
    QCCheckpoint, Commission, PerformanceMetric, Attendance, Leave,
    Payroll, Notification
)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'role', 'manager')
    list_filter = ('department', 'role', 'created_at')
    search_fields = ('name', 'email', 'designation')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'status', 'assigned_to', 'estimated_value')
    list_filter = ('status', 'created_at')
    search_fields = ('client_name', 'client_email', 'client_company')
    readonly_fields = ('created_at', 'updated_at', 'closed_date')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'completed_at')


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'email', 'phone')
    search_fields = ('name', 'company_name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'work_done')
    list_filter = ('date',)
    search_fields = ('employee__name', 'work_done')


@admin.register(QCCheckpoint)
class QCCheckpointAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'submitted_by', 'reviewed_by')
    list_filter = ('status', 'submitted_at')
    search_fields = ('submitted_by__name',)
    readonly_fields = ('submitted_at', 'reviewed_at')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('partner', 'lead', 'deal_value', 'commission_amount', 'status')
    list_filter = ('status', 'earned_date')
    search_fields = ('partner__name', 'lead__client_name')
    readonly_fields = ('commission_amount', 'created_at', 'updated_at')


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'target_value', 'achieved_value')
    list_filter = ('month',)
    search_fields = ('employee__name',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status')
    list_filter = ('date', 'status')
    search_fields = ('employee__name',)


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'from_date', 'to_date', 'status')
    list_filter = ('status', 'from_date')
    search_fields = ('employee__name', 'reason')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'net_salary')
    list_filter = ('month',)
    search_fields = ('employee__name',)
    readonly_fields = ('net_salary', 'created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__name', 'title')
    readonly_fields = ('created_at', 'read_at')
