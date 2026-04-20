from django.contrib import admin

# Register your models here.
from .models import CandidateProfile, ContactEnquiry, JobApplication, SupportTicket

admin.site.register(ContactEnquiry)
admin.site.register(SupportTicket)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "user", "created_at")
    search_fields = ("full_name", "phone", "user__email", "user__username")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job_title", "candidate", "department", "location", "status", "applied_at", "updated_at")
    list_filter = ("status", "department", "location")
    search_fields = ("job_title", "candidate__username", "candidate__email", "candidate__candidate_profile__full_name")
    readonly_fields = ("applied_at", "updated_at")
