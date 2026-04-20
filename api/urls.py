"""
REST API URL Configuration
Connects all viewsets and endpoints to routes
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from employees.api_views import (
    CustomTokenObtainPairView, register, logout, current_user,
    DepartmentViewSet, EmployeeViewSet, LeadViewSet, TaskViewSet,
    PartnerViewSet, DailyUpdateViewSet, QCCheckpointViewSet,
    CommissionViewSet, AttendanceViewSet, LeaveViewSet,
    PayrollViewSet, NotificationViewSet
)
# Initialize router
router = DefaultRouter()

# Register viewsets
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'daily-updates', DailyUpdateViewSet, basename='dailyupdate')
router.register(r'qc-checkpoints', QCCheckpointViewSet, basename='qccheckpoint')
router.register(r'commissions', CommissionViewSet, basename='commission')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leaves', LeaveViewSet, basename='leave')
router.register(r'payroll', PayrollViewSet, basename='payroll')
router.register(r'notifications', NotificationViewSet, basename='notification')

# Auth endpoints (not in router)
auth_patterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),
    path('auth/me/', current_user, name='current_user'),
]

# Combine all patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(auth_patterns)),
]
