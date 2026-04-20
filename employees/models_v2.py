"""
Enhanced Models for Production ScholVex System
Includes RBAC, Leads, Tasks, Partners, QC, and Commission Management
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ============================================
# DEPARTMENT & ROLE DEFINITIONS
# ============================================

class Department(models.Model):
    """Company departments including the new QC department"""
    
    DEPT_CHOICES = (
        ('MARKETING', 'Marketing'),
        ('SALES', 'Sales'),
        ('HR', 'Human Resources'),
        ('ACCOUNTS', 'Accounts'),
        ('TECHNICAL', 'Technical'),
        ('PRODUCTION', 'Production'),
        ('LEGAL', 'Legal'),
        ('QC', 'Quality Control'),
    )
    
    code = models.CharField(max_length=20, choices=DEPT_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Departments"


class Role(models.Model):
    """Role-based access control with permission bitmask"""
    
    ROLE_TYPES = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('TEAM_LEAD', 'Team Lead'),
        ('STAFF', 'Staff'),
        ('PARTNER', 'Channel Partner'),
        ('QC_MANAGER', 'QC Manager'),
        ('QC_ANALYST', 'QC Analyst'),
    )
    
    code = models.CharField(max_length=20, choices=ROLE_TYPES, unique=True)
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict, blank=True)  # Stores permission dict
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['code']


# ============================================
# EMPLOYEE MANAGEMENT
# ============================================

class Employee(models.Model):
    """Enhanced employee model with role-based access"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    designation = models.CharField(max_length=100)
    
    # Reporting hierarchy
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, 
                               blank=True, related_name='subordinates')
    
    # Compensation
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Profile
    photo = models.ImageField(upload_to='employees/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joining_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.role.name})"
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_employee_email')
        ]


# ============================================
# LEAD MANAGEMENT
# ============================================

class Lead(models.Model):
    """Lead management for marketing/sales teams"""
    
    STATUS_CHOICES = (
        ('NEW', 'New'),
        ('QUALIFIED', 'Qualified'),
        ('NEGOTIATING', 'Negotiating'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('CLOSED', 'Closed'),
    )
    
    SOURCE_CHOICES = (
        ('WEBSITE', 'Website'),
        ('REFERRAL', 'Referral'),
        ('EMAIL', 'Email'),
        ('CALL', 'Phone Call'),
        ('SOCIAL', 'Social Media'),
        ('PARTNER', 'Channel Partner'),
        ('OTHER', 'Other'),
    )
    
    id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=15)
    client_company = models.CharField(max_length=200, blank=True)
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    
    # Assignment
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    shared_partners = models.ManyToManyField(Employee, related_name='shared_leads', blank=True)
    
    # Details
    description = models.TextField(blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']


# ============================================
# TASK MANAGEMENT
# ============================================

class Task(models.Model):
    """Task and project management"""
    
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'Review'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    # Status tracking
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    
    # Dates
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Completion
    progress = models.IntegerField(default=0, help_text="0-100 percentage")
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    class Meta:
        ordering = ['-priority', 'due_date']


# ============================================
# CHANNEL PARTNER MANAGEMENT
# ============================================

class Partner(models.Model):
    """Channel partner for B2B lead sharing"""
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    )
    
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    company_name = models.CharField(max_length=200)
    
    # Contact info
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    assigned_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Commission
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00,
                                        help_text="Commission percentage (e.g., 5.00 for 5%)")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.company_name})"
    
    class Meta:
        ordering = ['name']


# ============================================
# DAILY WORK UPDATES (STAFF)
# ============================================

class DailyUpdate(models.Model):
    """Staff daily work update tracking"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_updates')
    date = models.DateField()
    
    # Work summary
    tasks_completed = models.IntegerField(default=0)
    leads_generated = models.IntegerField(default=0)
    meetings_scheduled = models.IntegerField(default=0)
    
    # Details
    work_summary = models.TextField(blank=True)
    achievements = models.TextField(blank=True, help_text="Major accomplishments")
    challenges = models.TextField(blank=True, help_text="Issues faced")
    next_day_plan = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_daily_update')
        ]


# ============================================
# QC DEPARTMENT (QUALITY CONTROL)
# ============================================

class QCCheckpoint(models.Model):
    """QC verification and approval checkpoints"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REWORK', 'Needs Rework'),
    )
    
    # Link to work item (task, lead, etc.)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='qc_checks')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='qc_checks')
    
    # QC Details
    submitted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='submitted_for_qc')
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='qc_reviews', limit_choices_to={'role__code__in': ['QC_MANAGER', 'QC_ANALYST']})
    
    # Checklist
    checklist_items = models.JSONField(default=list, blank=True)  # List of check items
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Feedback
    comments = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        item = self.task or self.lead
        return f"QC Review - {item} - {self.status}"
    
    class Meta:
        ordering = ['-submitted_at']


# ============================================
# COMMISSION TRACKING
# ============================================

class Commission(models.Model):
    """Track partner commissions"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
    )
    
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='commissions')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Commission calculation
    deal_value = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Dates
    earned_date = models.DateField()
    approved_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.partner.name} - ₹{self.commission_amount}"
    
    class Meta:
        ordering = ['-earned_date']


# ============================================
# PERFORMANCE & REPORTING
# ============================================

class PerformanceMetric(models.Model):
    """Track performance metrics per employee"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_metrics')
    month = models.CharField(max_length=7)  # YYYY-MM format
    
    # Sales metrics
    leads_generated = models.IntegerField(default=0)
    leads_closed = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Operational metrics
    tasks_completed = models.IntegerField(default=0)
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    # Quality metrics
    qc_pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.month}"
    
    class Meta:
        ordering = ['-month']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'month'], name='unique_monthly_metric')
        ]


# ============================================
# ATTENDANCE & LEAVE (Existing enhanced)
# ============================================

class Attendance(models.Model):
    """Attendance tracking"""
    
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
        ('HALF_DAY', 'Half Day'),
        ('WFH', 'Work from Home'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"
    
    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_attendance')
        ]


class Leave(models.Model):
    """Leave management"""
    
    TYPE_CHOICES = (
        ('CASUAL', 'Casual Leave'),
        ('SICK', 'Sick Leave'),
        ('EARNED', 'Earned Leave'),
        ('UNPAID', 'Unpaid Leave'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type}"
    
    class Meta:
        ordering = ['-from_date']


# ============================================
# PAYROLL (Existing enhanced)
# ============================================

class Payroll(models.Model):
    """Payroll and salary management"""
    
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('APPROVED', 'Approved'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=7)  # YYYY-MM
    
    # Salary components
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    pf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Final
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    paid_on = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.month}"
    
    class Meta:
        ordering = ['-month']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'month'], name='unique_monthly_payroll')
        ]


# ============================================
# NOTIFICATIONS
# ============================================

class Notification(models.Model):
    """System notifications"""
    
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.recipient.name} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']
