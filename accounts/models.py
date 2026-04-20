from django.conf import settings
from django.db import models

class ContactEnquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    organization = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models
import uuid

class SupportTicket(models.Model):
    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    product = models.CharField(max_length=100)
    priority = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = "SVX-" + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_id


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    qualification = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class JobApplication(models.Model):
    STATUS_APPLIED = "APPLIED"
    STATUS_SCREENING = "SCREENING"
    STATUS_SHORTLISTED = "SHORTLISTED"
    STATUS_INTERVIEW = "INTERVIEW"
    STATUS_SELECTED = "SELECTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_ON_HOLD = "ON_HOLD"

    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_SCREENING, "Screening"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_INTERVIEW, "Interview"),
        (STATUS_SELECTED, "Selected"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_ON_HOLD, "On Hold"),
    ]

    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_applications")
    job_title = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to="candidate_resumes/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["candidate", "job_title"], name="unique_candidate_job_application")
        ]

    def __str__(self):
        return f"{self.candidate} - {self.job_title}"

