from django.urls import path
from accounts import views

urlpatterns = [
    
# =========================
# LOGIN
# =========================

path('login/staff/', views.staff_login, name='staff_login'),
path('login/', views.login_view, name='login'),
path('login/partner/', views.partner_login, name='partner_login'),

path('login/client/', views.client_login, name='client_login'),
path('login/candidate/', views.candidate_login, name='candidate_login'),
path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
path('candidate/apply/', views.candidate_apply, name='candidate_apply'),
path('candidate/applications/', views.candidate_application_board, name='candidate_application_board'),

path('signup/client/', views.client_signup, name='client_signup'),
path('signup/candidate/', views.candidate_signup, name='candidate_signup'),

path('forgot-password/', views.forgot_password, name='forgot_password'),

# LOGOUT
path('logout/', views.logout_view, name='logout'),

# =========================
# PARTNER DASHBOARD
# =========================

path('partner/', views.partner_dashboard, name='partner_dashboard'),

path('partner/leads/', views.partner_leads, name='partner_leads'),
path('partner/customers/', views.partner_customers, name='partner_customers'),
path('partner/commission/', views.partner_commission, name='partner_commission'),
path('partner/reports/', views.partner_reports, name='partner_reports'),
path('partner/profile/', views.partner_profile, name='partner_profile'),

# =========================
# COMPANY PAGES
# =========================

path('about/', views.about, name='about'),
path('vision/', views.vision, name='vision'),
path('leadership/', views.leadership, name='leadership'),
path('clients/', views.clients, name='clients'),
path('partners/', views.partners, name='partners'),
path('careers/', views.careers, name='careers'),
path('company-profile/', views.company_profile, name='company_profile'),
path('presence/', views.presence, name='presence'),
path('strength/', views.strength, name='strength'),
path('terms/', views.terms, name='terms'),
path('privacy/', views.privacy, name='privacy'),
path('disclaimer/', views.disclaimer, name='disclaimer'),

# =========================
# PRODUCTS
# =========================

path('products/school-erp/', views.school_erp),
path('products/college-erp/', views.college_erp),
path('products/institute-erp/', views.institute_erp),
path('products/lms/', views.lms),
path('products/mobile-app/', views.mobile_app),

# technical

path('products/biometric/', views.biometric),
path('products/cctv/', views.cctv),
path('products/rfid/', views.rfid),
path('products/smart-class/', views.smart_class),
path('products/solar/', views.solar),
path('products/gps/', views.gps),

# communication

path('products/bulk-sms/', views.bulk_sms),
path('products/rcs-sms/', views.rcs_sms),
path('products/whatsapp/', views.whatsapp),
path('products/voice-call/', views.voice_call),
path('products/email/', views.email),
path('products/notification/', views.notification),

# essentials

path('products/id-cards/', views.id_cards),
path('products/uniforms/', views.uniforms),
path('products/tie-belt/', views.tie_belt),
path('products/bags/', views.bags),
path('products/notebooks/', views.notebooks),
path('products/diaries/', views.diaries),

# printing

path('products/textbooks/', views.textbooks),
path('products/certificates/', views.certificates),
path('products/report-cards/', views.report_cards),
path('products/mementos/', views.mementos),
path('products/printing/', views.printing),

# infrastructure

path('products/furniture/', views.furniture),
path('products/lab-setup/', views.lab_setup),
path('products/smart-classroom/', views.smart_classroom),
path('products/computer-lab/', views.computer_lab),

# =========================
# SOLUTIONS
# =========================

path('solutions/school/', views.school_solution, name='school_solution'),
path('solutions/college/', views.college_solution, name='college_solution'),
path('solutions/institute/', views.institute_solution, name='institute_solution'),

path('solutions/smart-campus/', views.smart_campus),
path('solutions/digital-communication/', views.digital_communication),
path('solutions/communication/', views.communication),
path('solutions/automation/', views.automation),

path('solutions/student-management/', views.student_management),
path('solutions/staff-management/', views.staff_management),
path('solutions/attendance/', views.attendance),
path('solutions/fee-management/', views.fee_management),

# ================= SERVICES =================

path('services/website-development/', views.website_development),
path('services/app-development/', views.app_development),
path('services/erp-setup/', views.erp_setup),
path('services/portal-development/', views.portal_development),

# TECHNICAL

path('services/installation/', views.installation),
path('services/networking/', views.networking),
path('services/server-setup/', views.server_setup),
path('services/smart-class-setup/', views.smart_class_setup),

# ADMISSION SUPPORT

path('services/student-counselling/', views.student_counselling),
path('services/admission-campaign/', views.admission_campaign),
path('services/lead-generation/', views.lead_generation),
path('services/seat-filling/', views.seat_filling),

# EVENT MANAGEMENT

path('services/annual-day/', views.annual_day),
path('services/sports-day/', views.sports_day),
path('services/college-fest/', views.college_fest),
path('services/seminars/', views.seminars),

# STAFFING

path('services/teaching-staff/', views.teaching_staff),
path('services/non-teaching-staff/', views.non_teaching_staff),
path('services/admin-staff/', views.admin_staff),
path('services/marketing-staff/', views.marketing_staff),

# DIGITAL MARKETING

path('services/admission-marketing/', views.admission_marketing),
path('services/social-media/', views.social_media),
path('services/seo/', views.seo),
path('services/paid-ads/', views.paid_ads),
path('services/whatsapp-sms/', views.whatsapp_sms),
path('services/branding/', views.branding),
path('services/website-marketing/', views.website_marketing),
path('services/analytics/', views.analytics),

# ACADEMIC

path('services/tutors/', views.tutors),
path('services/guest-faculty/', views.guest_faculty),
path('services/trainers/', views.trainers),
path('services/coaching-faculty/', views.coaching_faculty),

# MAINTENANCE

path('services/electrician/', views.electrician),
path('services/plumbing/', views.plumbing),
path('services/painting/', views.painting),
path('services/renovations/', views.renovations),
path('services/amc/', views.amc),


# MANAGEMENT

path('management/school/', views.school_management, name='school_management'),
path('management/college/', views.college_management, name='college_management'),
path('management/institute/', views.institute_management, name='institute_management'),

path('management/hr/', views.hr_management, name='hr_management'),
path('management/accounts/', views.accounts_management, name='accounts_management'),
path('management/admissions/', views.admission_management, name='admission_management'),

path('management/transport/', views.transport_management, name='transport_management'),
path('management/hostel/', views.hostel_management, name='hostel_management'),
path('management/facility/', views.facility_management, name='facility_management'),
path('management/security/', views.security_management, name='security_management'),


# SUPPORT PAGES
path('support/helpdesk/', views.helpdesk, name='helpdesk'),
path('support/ticket-support/', views.ticket_support, name='ticket_support'),
path('support/remote-support/', views.remote_support, name='remote_support'),

path('support/amc-plans/', views.amc_plans, name='amc_plans'),
path('support/preventive-maintenance/', views.preventive_maintenance, name='preventive_maintenance'),
path('support/onsite-support/', views.onsite_support, name='onsite_support'),

path('support/raise-ticket/', views.raise_ticket, name='raise_ticket'),
path('support/track-ticket/', views.track_ticket, name='track_ticket'),
path('support/service-request/', views.service_request, name='service_request'),

path('support/user-manuals/', views.user_manuals, name='user_manuals'),
path('support/documentation/', views.documentation, name='documentation'),
path('support/software-downloads/', views.software_downloads, name='software_downloads'),

path('ai-chat/', views.ai_chat, name='ai_chat'),

path('contact-submit/', views.contact_submit, name='contact_submit'),

path('submit-ticket/', views.submit_ticket, name='submit_ticket'),

path('track-ticket/', views.track_ticket, name='track_ticket'),

]
