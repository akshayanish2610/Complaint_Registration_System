from django.urls import path
from .views import *
from .views import generate_report

urlpatterns = [
     path('', user_login, name='user_login'),
     path('logout/', user_logout, name='user_logout'),
     path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),
     path('student/dashboard/', student_dashboard, name='student_dashboard'),
     path('staff/create_student/', create_student, name='create_student'),
     path('student/profile/', student_profile, name='student_profile'),
     path('student/edit_profile/', student_edit_profile, name='student_edit_profile'),
     path('student/register_complaint/', student_register_complaint, name='student_register_complaint'),
     path('staff/complaint/display/', staff_complaint_display, name='staff_complaint_display'),
     path('staff/students/', student_list, name='student_list'),
     path('add_staff_meeting/', add_staff_meeting, name='add_staff_meeting'),
     path('view_staff_meetings/', view_staff_meetings, name='view_staff_meetings'),
     path('analytics/', analytics, name='analytics'),
     path('generate_report/', generate_report, name='generate_report'),
     path('edit_student/<str:username>/', edit_student, name='edit_student'),
     path('delete_student/<str:username>/', delete_student, name='delete_student'),
     path('student_complaint_history/', student_complaint_history, name='student_complaint_history'),


]