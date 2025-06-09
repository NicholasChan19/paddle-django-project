"""
URL configuration for paddle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


    path('admin/', admin.site.urls), -> buat admin page dari django
"""
from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),

    # path('test/', views.test_page, name='test'),
    path('teacher/home/', views.teacher_home, name='teacher_home'),
    path('admins/home/', views.admin_home, name='admin_home'),
    #path('parent/home/', views.parent_home, name='parent_home'),

    #sessions
    path('admins/sessions/', views.admin_sessions, name='admin_sessions'),
    path('sessions/create/', views.add_session, name='add_session'),
    path('sessions/<int:session_id>/', views.session_details, name='session_details'),
    path('sessions/<int:session_id>/edit/', views.edit_session, name='edit_session'),
    path('sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),

    #summaries
    path('admins/summaries/', views.admin_summaries, name='admin_summaries'),
    path('admins/summaries/pending_summaries', views.admin_pending_summaries, name='admin_pending_summaries'),

    #students
    path('admins/students', views.admin_students, name='admin_students'),
    path('admins/students/<int:student_id>/', views.student_details, name='student_details'),
    path('students/create/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),

    #teachers
    path('admins/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admins/teachers/<int:teacher_id>/', views.teacher_details, name='teacher_details'),
    path('teachers/create/', views.add_teacher, name='add_teacher'),
    path('teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/<int:teacher_id>/delete/', views.delete_teacher, name='delete_teacher'),

    #courses
    path('admins/courses/', views.admin_courses, name='admin_courses'),
    path('admins/courses/create/', views.create_course, name='create_course'),
    path('admins/courses/<int:course_id>/', views.course_list, name='course_list'),
    path('course/<int:course_id>/add-material/', views.add_material, name='add_material'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('material/<int:material_id>/edit/', views.edit_material, name='edit_material'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),

    #payments
    path('admins/payments', views.admin_payments, name='admin_payments'),
    path('admins/payments/payment_requests', views.admin_payment_requests, name='admin_payment_requests'),
    
    #certificates
    path('admins/certificates', views.admin_certificates, name='admin_certificates'),
    path('admins/certificates/pending_certificates', views.admin_pending_certificates, name='admin_pending_certificates'),
    path('admins/certificates/unconfirmed_certificates', views.admin_unconfirmed_certificates, name='admin_unconfirmed_certificates'),
    path('admins/pending_summaries', views.pending_summaries, name='pending_summaries'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
