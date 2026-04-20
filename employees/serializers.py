"""
Production-Ready REST API Serializers
Handles JSON serialization for all models with validation
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models_v2 import (
    Department, Role, Employee, Lead, Task, Partner,
    DailyUpdate, QCCheckpoint, Commission, PerformanceMetric,
    Attendance, Leave, Payroll, Notification
)


# ============================================
# AUTH SERIALIZERS
# ============================================

class UserSerializer(serializers.ModelSerializer):
    """User model serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """Create user with password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data.get('password') != data.pop('password_confirm', None):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ============================================
# DEPARTMENT & ROLE SERIALIZERS
# ============================================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'permissions', 'created_at']
        read_only_fields = ['id', 'created_at']


# ============================================
# EMPLOYEE SERIALIZERS
# ============================================

class EmployeeListSerializer(serializers.ModelSerializer):
    """Employee list view (minimal data)"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'phone', 'designation',
            'department', 'department_name',
            'role', 'role_name',
            'manager', 'manager_name',
            'salary', 'is_active', 'joining_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Employee detail view (full data)"""
    department = DepartmentSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    manager = EmployeeListSerializer(read_only=True)
    subordinates = EmployeeListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'name', 'email', 'phone', 'designation',
            'department', 'role', 'manager', 'subordinates',
            'salary', 'photo', 'is_active', 'joining_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/update employee"""
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'phone', 'designation',
            'department', 'role', 'manager', 'salary', 'joining_date'
        ]
    
    def validate_email(self, value):
        if self.instance is None and Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("Employee with this email already exists")
        return value


# ============================================
# LEAD SERIALIZERS
# ============================================

class LeadListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'client_name', 'client_email', 'client_company',
            'source', 'status', 'assigned_to', 'assigned_to_name',
            'estimated_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadDetailSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeListSerializer(read_only=True)
    shared_partners = EmployeeListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'client_name', 'client_email', 'client_phone', 'client_company',
            'source', 'status', 'assigned_to', 'shared_partners',
            'description', 'estimated_value',
            'created_at', 'updated_at', 'closed_date'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'closed_date']


class LeadCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'client_name', 'client_email', 'client_phone', 'client_company',
            'source', 'status', 'assigned_to', 'description', 'estimated_value'
        ]


# ============================================
# TASK SERIALIZERS
# ============================================

class TaskListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'status', 'progress',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'due_date', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeListSerializer(read_only=True)
    created_by = EmployeeListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'progress',
            'assigned_to', 'created_by', 'due_date', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'status', 'progress',
            'assigned_to', 'due_date'
        ]


# ============================================
# PARTNER SERIALIZERS
# ============================================

class PartnerSerializer(serializers.ModelSerializer):
    assigned_manager_name = serializers.CharField(source='assigned_manager.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Partner
        fields = [
            'id', 'name', 'email', 'phone', 'company_name',
            'address', 'city', 'state',
            'status', 'assigned_manager', 'assigned_manager_name',
            'commission_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================
# DAILY UPDATE SERIALIZERS
# ============================================

class DailyUpdateSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = DailyUpdate
        fields = [
            'id', 'employee', 'employee_name', 'date',
            'tasks_completed', 'leads_generated', 'meetings_scheduled',
            'work_summary', 'achievements', 'challenges', 'next_day_plan',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee', 'created_at', 'updated_at']


# ============================================
# QC SERIALIZERS
# ============================================

class QCCheckpointSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.name', read_only=True, allow_null=True)
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    lead_name = serializers.CharField(source='lead.client_name', read_only=True, allow_null=True)
    
    class Meta:
        model = QCCheckpoint
        fields = [
            'id', 'task', 'task_title', 'lead', 'lead_name',
            'submitted_by', 'submitted_by_name',
            'reviewed_by', 'reviewed_by_name',
            'checklist_items', 'status', 'comments', 'feedback',
            'submitted_at', 'reviewed_at', 'created_at'
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'created_at']


# ============================================
# COMMISSION SERIALIZERS
# ============================================

class CommissionListSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    lead_info = serializers.SerializerMethodField()
    
    def get_lead_info(self, obj):
        if obj.lead:
            return f"{obj.lead.client_name} (₹{obj.lead.estimated_value})"
        return None
    
    class Meta:
        model = Commission
        fields = [
            'id', 'partner', 'partner_name', 'lead', 'lead_info',
            'deal_value', 'commission_rate', 'commission_amount',
            'status', 'earned_date', 'paid_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============================================
# PERFORMANCE SERIALIZERS
# ============================================

class PerformanceMetricSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'employee', 'employee_name', 'month',
            'leads_generated', 'leads_closed', 'revenue_generated',
            'tasks_completed', 'attendance_score', 'qc_pass_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================
# ATTENDANCE SERIALIZERS
# ============================================

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date',
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================
# LEAVE SERIALIZERS
# ============================================

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_name', 'leave_type',
            'from_date', 'to_date', 'reason', 'status',
            'approved_by', 'approved_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'approved_by', 'created_at', 'updated_at']


# ============================================
# PAYROLL SERIALIZERS
# ============================================

class PayrollListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'month',
            'basic', 'hra', 'bonus', 'pf', 'tax', 'net_salary',
            'status', 'paid_on', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PayrollDetailSerializer(serializers.ModelSerializer):
    employee = EmployeeListSerializer(read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'month',
            'basic', 'hra', 'bonus', 'pf', 'tax', 'net_salary',
            'status', 'paid_on', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================
# NOTIFICATION SERIALIZERS
# ============================================

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'title', 'message',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'created_at']


# ============================================
# LOGIN RESPONSE SERIALIZER
# ============================================

class LoginResponseSerializer(serializers.Serializer):
    """Response for login endpoint"""
    token = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    role = serializers.CharField()
    department = serializers.CharField()
    employee_id = serializers.IntegerField()
