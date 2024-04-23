from ultimaterent import views
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from ultimaterent.views import reject_visit_schedule, accept_visit_schedule, user_schedule_requests, submit_offer, \
    agent_login, agent_dashboard_view, activate_account, agent_signup, admin_dashboard, \
    approve_agent, reject_agent

urlpatterns = [
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('approve-agent/<int:agent_id>/', approve_agent, name='approve_agent'),
    path('reject-agent/<int:agent_id>/', reject_agent, name='reject_agent'),

    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('profile/', views.profile_view, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('loan/', views.loan, name='loan'),
    path('guide/', views.guide, name='guide'),
    path('add_property/', views.add_property_view, name='add_property'),
    path('properties/', views.property_list, name='property_list'),
    path('search/', views.search, name='search'),
    path('property/<int:id>/', views.property_detail, name='property_detail'),
    path('signup/', views.signup, name="signup"),  # Added trailing slash
    path('signin/', views.signin, name="signin"),  # Added trailing slash
    path('signout/', views.signout, name="signout"),  # Added trailing slash
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('property/edit/<int:id>/', views.edit_property, name='edit_property'),
    path('property/delete/<int:id>/', views.delete_property, name='delete_property'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('schedule-visit/<int:property_id>/', views.schedule_visit, name='schedule-visit'),
    path('visit-schedules/', views.visit_schedule_list, name='visit_schedule_list'),
    path('schedules/<int:schedule_id>/accept/', accept_visit_schedule, name='accept_visit_schedule'),
    path('schedules/<int:schedule_id>/reject/', reject_visit_schedule, name='reject_visit_schedule'),
    path('my-schedule-requests/', user_schedule_requests, name='user_schedule_requests'),
    path('properties/<int:property_id>/submit_offer/', submit_offer, name='submit_offer'),
    path('offer-list/', views.offer_list, name='offer_list'),
    path('payment/', views.payment_form, name='payment_form'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),  # You need to create this view
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    path('agent/login/', agent_login, name='agent_login'),
    path('agent/dashboard/', agent_dashboard_view, name='agent_dashboard'),
    path('schedule_appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('appointment-success/', views.appointment_success, name='appointment_success'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('agent/signup/', agent_signup, name='agent_signup'),
    path('appointment/<int:appointment_id>/accept/', views.accept_appointment, name='accept_appointment'),
    path('appointment/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),



    # ... other patterns ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
