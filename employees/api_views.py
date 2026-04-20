"""
Production-Ready REST API Views
Handles all business logic, permissions, and data retrieval
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
import logging

from .models_v2 import (
    Department, Role, Employee, Lead, Task, Partner,
    DailyUpdate, QCCheckpoint, Commission, PerformanceMetric,
    Attendance, Leave, Payroll, Notification
)
from .serializers import (
    DepartmentSerializer, RoleSerializer, EmployeeListSerializer,
    EmployeeDetailSerializer, EmployeeCreateUpdateSerializer,
    LeadListSerializer, LeadDetailSerializer, LeadCreateUpdateSerializer,
    TaskListSerializer, TaskDetailSerializer, TaskCreateUpdateSerializer,
    PartnerSerializer, DailyUpdateSerializer, QCCheckpointSerializer,
    CommissionListSerializer, PerformanceMetricSerializer,
    AttendanceSerializer, LeaveSerializer, PayrollListSerializer,
    PayrollDetailSerializer, NotificationSerializer, LoginResponseSerializer,
    UserSerializer, UserCreateSerializer
)
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


# ============================================
# PAGINATION
# ============================================

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================
# PERMISSIONS
# ============================================

class IsAdmin(IsAuthenticated):
    """Only admin users"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.employee.role.code == 'ADMIN'


class IsQCStaff(IsAuthenticated):
    """QC Manager or QC Analyst"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.employee.role.code in ['QC_MANAGER', 'QC_ANALYST']


class IsPartner(IsAuthenticated):
    """Channel partner role"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.employee.role.code == 'PARTNER'


# ============================================
# AUTH ENDPOINTS
# ============================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login that includes user details"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'User account is inactive'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get employee details
        try:
            employee = user.employee
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'designation': employee.designation,
                'department': employee.department.name if employee.department else None,
                'role': employee.role.code if employee.role else None
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register new user"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user"""
    # Token invalidation handled by frontend
    return Response({
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user details"""
    user = request.user
    employee = user.employee
    
    data = {
        'user': UserSerializer(user).data,
        'employee': EmployeeDetailSerializer(employee).data
    }
    
    return Response(data, status=status.HTTP_200_OK)


# ============================================
# DEPARTMENT VIEWSET
# ============================================

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Department listing (read-only)"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination


# ============================================
# EMPLOYEE VIEWSET
# ============================================

class EmployeeViewSet(viewsets.ModelViewSet):
    """Employee management"""
    queryset = Employee.objects.select_related('department', 'role', 'manager').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'designation']
    ordering_fields = ['name', 'joining_date', '-created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'retrieve':
            return EmployeeDetailSerializer
        else:
            return EmployeeCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's employee profile"""
        employee = request.user.employee
        serializer = EmployeeDetailSerializer(employee)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """Get subordinates of a manager"""
        employee = self.get_object()
        subordinates = employee.subordinates.all()
        serializer = EmployeeListSerializer(subordinates, many=True)
        return Response(serializer.data)


# ============================================
# LEAD VIEWSET
# ============================================

class LeadViewSet(viewsets.ModelViewSet):
    """Lead management"""
    queryset = Lead.objects.select_related('assigned_to').prefetch_related('shared_partners').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['client_name', 'client_email', 'client_company']
    ordering_fields = ['created_at', 'estimated_value', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        elif self.action == 'retrieve':
            return LeadDetailSerializer
        else:
            return LeadCreateUpdateSerializer
    
    def get_queryset(self):
        """Filter leads based on role"""
        user = self.request.user
        employee = user.employee
        
        # Admin sees all
        if employee.role.code == 'ADMIN':
            return self.queryset
        
        # Partners see shared leads
        if employee.role.code == 'PARTNER':
            return self.queryset.filter(
                Q(shared_partners=employee) | Q(assigned_to=employee)
            )
        
        # Staff sees assigned leads
        return self.queryset.filter(assigned_to=employee)
    
    def perform_create(self, serializer):
        """Auto-assign created leads to current user if not specified"""
        if not serializer.validated_data.get('assigned_to'):
            serializer.validated_data['assigned_to'] = self.request.user.employee
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def share_with_partner(self, request, pk=None):
        """Share lead with channel partner"""
        lead = self.get_object()
        partner_id = request.data.get('partner_id')
        
        partner = get_object_or_404(Employee, id=partner_id, role__code='PARTNER')
        lead.shared_partners.add(partner)
        
        # Create notification
        Notification.objects.create(
            recipient=partner,
            title='New Lead Shared',
            message=f'Lead {lead.client_name} has been shared with you'
        )
        
        return Response({'status': 'Lead shared successfully'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update lead status"""
        lead = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Lead.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lead.status = new_status
        if new_status == 'WON':
            lead.closed_date = datetime.now()
        lead.save()
        
        return Response(LeadDetailSerializer(lead).data)


# ============================================
# TASK VIEWSET
# ============================================

class TaskViewSet(viewsets.ModelViewSet):
    """Task management"""
    queryset = Task.objects.select_related('assigned_to', 'created_by').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'due_date', 'status']
    ordering = ['-priority', 'due_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        else:
            return TaskCreateUpdateSerializer
    
    def get_queryset(self):
        """Filter tasks based on role"""
        user = self.request.user
        employee = user.employee
        
        # Admin sees all
        if employee.role.code == 'ADMIN':
            return self.queryset
        
        # Others see tasks assigned to them or created by them
        return self.queryset.filter(
            Q(assigned_to=employee) | Q(created_by=employee)
        )
    
    def perform_create(self, serializer):
        """Auto-set creator"""
        serializer.save(created_by=self.request.user.employee)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'COMPLETED'
        task.progress = 100
        task.completed_at = datetime.now()
        task.save()
        
        return Response(TaskDetailSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update task progress"""
        task = self.get_object()
        progress = request.data.get('progress', 0)
        
        if not 0 <= progress <= 100:
            return Response(
                {'error': 'Progress must be 0-100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.progress = progress
        if progress == 100:
            task.status = 'COMPLETED'
            task.completed_at = datetime.now()
        task.save()
        
        return Response(TaskDetailSerializer(task).data)


# ============================================
# PARTNER VIEWSET
# ============================================

class PartnerViewSet(viewsets.ModelViewSet):
    """Channel partner management"""
    queryset = Partner.objects.select_related('assigned_manager').all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'company_name', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()


# ============================================
# DAILY UPDATE VIEWSET
# ============================================

class DailyUpdateViewSet(viewsets.ModelViewSet):
    """Daily work updates"""
    queryset = DailyUpdate.objects.select_related('employee').all()
    serializer_class = DailyUpdateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering_fields = ['date', '-created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter based on role"""
        user = self.request.user
        employee = user.employee
        
        # Admin sees all
        if employee.role.code == 'ADMIN':
            return self.queryset
        
        # Others see only their own
        return self.queryset.filter(employee=employee)
    
    def perform_create(self, serializer):
        """Auto-set employee to current user"""
        serializer.save(employee=self.request.user.employee)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's update for current user"""
        today = datetime.now().date()
        update = DailyUpdate.objects.filter(
            employee=request.user.employee,
            date=today
        ).first()
        
        if not update:
            return Response({'detail': 'No update for today'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DailyUpdateSerializer(update)
        return Response(serializer.data)


# ============================================
# QC CHECKPOINT VIEWSET
# ============================================

class QCCheckpointViewSet(viewsets.ModelViewSet):
    """QC verification and approval"""
    queryset = QCCheckpoint.objects.select_related('submitted_by', 'reviewed_by').all()
    serializer_class = QCCheckpointSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['status', 'submitted_at']
    ordering = ['-submitted_at']
    
    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            return [IsQCStaff()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve QC checkpoint"""
        checkpoint = self.get_object()
        checkpoint.status = 'APPROVED'
        checkpoint.reviewed_by = request.user.employee
        checkpoint.reviewed_at = datetime.now()
        checkpoint.save()
        
        # Notify submitter
        Notification.objects.create(
            recipient=checkpoint.submitted_by,
            title='QC Approved',
            message='Your work has been approved by QC'
        )
        
        return Response(QCCheckpointSerializer(checkpoint).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject QC checkpoint"""
        checkpoint = self.get_object()
        checkpoint.status = 'REWORK'
        checkpoint.reviewed_by = request.user.employee
        checkpoint.reviewed_at = datetime.now()
        checkpoint.feedback = request.data.get('feedback', '')
        checkpoint.save()
        
        # Notify submitter
        Notification.objects.create(
            recipient=checkpoint.submitted_by,
            title='QC Rejected - Rework Needed',
            message=f'Feedback: {checkpoint.feedback}'
        )
        
        return Response(QCCheckpointSerializer(checkpoint).data)


# ============================================
# COMMISSION VIEWSET
# ============================================

class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Commission tracking"""
    queryset = Commission.objects.select_related('partner', 'lead').all()
    serializer_class = CommissionListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering_fields = ['earned_date', 'commission_amount', 'status']
    ordering = ['-earned_date']
    
    def get_queryset(self):
        """Filter based on role"""
        user = self.request.user
        employee = user.employee
        
        # Admin sees all
        if employee.role.code == 'ADMIN':
            return self.queryset
        
        # Partners see only their own
        try:
            partner = Partner.objects.get(email=employee.email)
            return self.queryset.filter(partner=partner)
        except Partner.DoesNotExist:
            return Commission.objects.none()


# ============================================
# ATTENDANCE VIEWSET
# ============================================

class AttendanceViewSet(viewsets.ModelViewSet):
    """Attendance management"""
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering_fields = ['date']
    ordering = ['-date']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'])
    def mark_today(self, request):
        """Mark attendance for today"""
        today = datetime.now().date()
        employee = request.user.employee
        
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'PRESENT'}
        )
        
        if not created:
            attendance.status = request.data.get('status', 'PRESENT')
            attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# LEAVE VIEWSET
# ============================================

class LeaveViewSet(viewsets.ModelViewSet):
    """Leave management"""
    queryset = Leave.objects.select_related('employee', 'approved_by').all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering_fields = ['from_date', 'status']
    ordering = ['-from_date']
    
    def get_queryset(self):
        """Filter based on role"""
        user = self.request.user
        employee = user.employee
        
        # Admin sees all
        if employee.role.code == 'ADMIN':
            return self.queryset
        
        # Managers see their team's leaves
        if employee.role.code in ['MANAGER', 'TEAM_LEAD']:
            return self.queryset.filter(employee__manager=employee) | self.queryset.filter(employee=employee)
        
        # Others see their own
        return self.queryset.filter(employee=employee)
    
    def perform_create(self, serializer):
        """Auto-set employee"""
        serializer.save(employee=self.request.user.employee)


# ============================================
# PAYROLL VIEWSET
# ============================================

class PayrollViewSet(viewsets.ReadOnlyModelViewSet):
    """Payroll management"""
    queryset = Payroll.objects.select_related('employee').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering_fields = ['month', 'net_salary']
    ordering = ['-month']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PayrollDetailSerializer
        return PayrollListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def my_payroll(self, request):
        """Get current user's payroll"""
        payroll = Payroll.objects.filter(employee=request.user.employee)
        page = self.paginate_queryset(payroll)
        if page is not None:
            serializer = PayrollListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayrollListSerializer(payroll, many=True)
        return Response(serializer.data)


# ============================================
# NOTIFICATION VIEWSET
# ============================================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """Notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get only current user's notifications"""
        return Notification.objects.filter(recipient=self.request.user.employee)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = datetime.now()
        notification.save()
        
        return Response(NotificationSerializer(notification).data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        notifications = Notification.objects.filter(
            recipient=request.user.employee,
            is_read=False
        )
        count = notifications.update(
            is_read=True,
            read_at=datetime.now()
        )
        
        return Response({'marked_as_read': count})
