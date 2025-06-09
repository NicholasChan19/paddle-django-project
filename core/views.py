from django.shortcuts import render, redirect, get_object_or_404
from core.models import User  
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from .models import *
from django.db.models import Count,OuterRef, Subquery, Prefetch
from .forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.utils.timezone import now

DAYS_OF_WEEK = [
    ('', 'All days'), 
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email not found.')
            return redirect('login')

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_home')
            elif user.role == 'teacher':
                return redirect('teacher_home')
            elif user.role == 'student':
                return redirect('parent_home')
            else:
                messages.error(request, 'Unknown role.')
        else:
            messages.error(request, 'Wrong password.')

        return redirect('login')

    return render(request, 'login.html')

# def test_page(request):
#     return render(request, 'base/teacher_base.html')

def teacher_home(request):
    return render(request, 'pages/teacher_home.html')

def admin_home(request):
    return render(request, 'pages/admin_home.html')

def admin_sessions(request):
    sort = request.GET.get('sort', 'date')
    direction = request.GET.get('direction', 'asc')
    
    selected_days = request.GET.getlist('days')  #klo multiple days
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    allowed_sort_fields = ['date', 'time', 'num_students']
    if sort not in allowed_sort_fields:
        sort = 'date'
    order_by_field = f'-{sort}' if direction == 'desc' else sort

    sessions = Session.objects.annotate(num_students=Count('summary'))

    #start date
    if start_date:
        try:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            sessions = sessions.filter(date__gte=start_date_obj)
        except ValueError:
            pass

    #end date
    if end_date:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            sessions = sessions.filter(date__lte=end_date_obj)
        except ValueError:
            pass

    days_map = {
        'Monday': 2,
        'Tuesday': 3,
        'Wednesday': 4,
        'Thursday': 5,
        'Friday': 6,
        'Saturday': 7,
        'Sunday': 1,
    }

    #filter by days
    if selected_days:
        week_days = [days_map[day] for day in selected_days if day in days_map]
        if week_days:
            sessions = sessions.filter(date__week_day__in=week_days)

    sessions = sessions.order_by(order_by_field)

    context = {
        'sessions': sessions,
        'sort': sort,
        'direction': direction,
        'selected_days': selected_days,
        'start_date': start_date,
        'end_date': end_date,
        'DAYS_OF_WEEK': DAYS_OF_WEEK,
    }
    return render(request, 'pages/admin_sessions.html', context)

def add_session(request):

    students = Student.objects.select_related('user').all()
    preselected_ids = []

    if request.method == 'POST':
        form = SessionForm(request.POST)
        selected_ids_str = request.POST.get('selected_students', '')
        selected_ids = selected_ids_str.split(',') if selected_ids_str else []
        add_scheduled = request.POST.get('add_scheduled') == '1'

        if form.is_valid():
            session = form.save()

            if add_scheduled:
                today = now().strftime('%A').lower()
                scheduled_students = Student.objects.filter(schedule__day=today)
                selected_ids = [str(s.user.id) for s in scheduled_students]

    
            session.students.set(Student.objects.filter(user__id__in=selected_ids))

            messages.success(request, "Session created successfully!")
            return redirect('admin_sessions')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = SessionForm()

    return render(request, 'pages/add_session.html', {
        'form': form,
        'students': students,
        'preselected_ids': preselected_ids,
    })

def session_details(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    students = session.summary_set.all()
    return render(request, 'pages/session_details.html', {'session': session, 'students': students})

def edit_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, f"Session on {session.date.strftime('%B %d, %Y')} was updated successfully.")
            return redirect('admin_sessions')
    else:
        form = SessionForm(instance=session)
    return render(request, 'pages/edit_session.html', {'form': form, 'session': session})

def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        session_date = session.date.strftime('%B %d, %Y')
        session.delete()
        messages.success(request, f"Session on {session_date} was deleted.")
        return redirect('admin_sessions')
    return redirect('admin_sessions')

def admin_summaries(request):
    summaries = Summary.objects.select_related('material__course').all() #ini ambil semua material yg related to thecourse

    for summary in summaries:
        next_material = Material.objects.filter( #filter yg belong to course = summary.material.course, order__gt itu buat cari yg next materinya berdasarkan order
            course=summary.material.course, #cari course dari material yg ada di summary tersebut
            order__gt=summary.material.order,
            isRemoved=False
        ).order_by('order').first()
        summary.next_material = next_material

    return render(request, 'pages/admin_summaries.html', {'summaries': summaries})


def admin_pending_summaries(request):
    return render(request, 'pages/admin_pending_summaries.html')

def admin_students(request):
    #parameter utk sortnya
    sort = request.GET.get('sort', 'student')
    direction = request.GET.get('direction', 'asc')
    order_prefix = '' if direction == 'asc' else '-'

    #search/filter inputs
    search = request.GET.get('search', '')
    selected_courses = request.GET.getlist('course')
    selected_schedules = request.GET.getlist('schedule')

    #ambil latest summary pake -datecreated yg paling baru
    latest_summaries = Summary.objects.filter(student=OuterRef('pk')).order_by('-dateCreated')

    #ambil semua students
    students = Student.objects.prefetch_related(
        Prefetch('schedule_set', queryset=Schedule.objects.all())
    ).annotate(
        latest_material_name=Subquery(latest_summaries.values('material__name')[:1]),
        latest_summary_date=Subquery(latest_summaries.values('dateCreated')[:1])
    )

    #filtering
    if search:
        students = students.filter(user__name__icontains=search)


    if selected_schedules:
        students = students.filter(schedule__day__in=selected_schedules).distinct()

    #sorting
    sort_fields = {
        'student': 'user__name',
        'last_meeting': 'latest_summary_date',
    }
    sort_field = sort_fields.get(sort, 'user__name')
    students = students.order_by(f"{order_prefix}{sort_field}")

    #ambil data tambahan buat filter
    all_courses = Course.objects.all()

    return render(request, 'pages/admin_students.html', {
        'students': students,
        'sort': sort,
        'direction': direction,
        'search': search,
        'DAYS_OF_WEEK': DAYS_OF_WEEK,
        'selected_courses': selected_courses,
        'selected_schedules': selected_schedules,
    })

def add_student(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST, request.FILES)

        if user_form.is_valid() and student_form.is_valid(): #klo udh sesuai field baru dia return true
            user = user_form.save(commit=False)
            user.username = user.email
            user.set_password(user.password)
            user.role = 'student'
            user.status = 'active'
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.save()

            for day in student_form.cleaned_data['schedule']:
                Schedule.objects.create(student=student, day=day)

            messages.success(request, f"Student {user.name} created successfully!")
            return redirect('admin_students') 
        else:
            messages.error(request, "Failed to save. Please enter the fields appropriately.")
    else:
        user_form = UserForm()
        student_form = StudentForm()

    return render(request, 'pages/add_student.html', {
        'user_form': user_form,
        'student_form': student_form,
    })

def student_details(request, student_id):
    student = get_object_or_404(Student, pk=student_id) #fetch dr database, klo gaada bakal 404 not found
    certificates = Certificate.objects.filter(student=student)
    latest_payment = Payment.objects.filter(student=student).order_by('-dueDate').first()
    summaries = Summary.objects.select_related('material__course').filter(student=student).order_by('-dateCreated')[:2] #ini ambil semua material yg related to thecourse filter student itu buat spesifik murid itu
    schedules = Schedule.objects.filter(student=student)

    for summary in summaries:
        next_material = Material.objects.filter( #filter yg belong to course = summary.material.course, order__gt itu buat cari yg next materinya berdasarkan order
            course=summary.material.course, #cari course dari material yg ada di summary tersebut
            order__gt=summary.material.order,
            isRemoved=False
        ).order_by('order').first()
        summary.next_material = next_material
        
    context = {
        'student': student,
        'certificates': certificates,
        'latest_payment': latest_payment,
        'summaries': summaries,
        'schedules': schedules,
    }

    return render(request, 'pages/student_details.html', context)

def edit_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    user = student.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        student_form = StudentForm(request.POST, request.FILES, instance=student)

        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            #hash ulang password
            if 'password' in user_form.cleaned_data and user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.save()

            #schedule nya dibikin ulang
            Schedule.objects.filter(student=student).delete()
            for day in student_form.cleaned_data['schedule']:
                Schedule.objects.create(student=student, day=day)

            messages.success(request, f"Student {user.name} edited successfully!")
            return redirect('admin_students')
        else:
            messages.error(request, "Failed to save. Please enter the fields appropriately.")
    else:
        user_form = UserForm(instance=user)
        initial_schedule = list(student.schedule_set.values_list('day', flat=True))
        student_form = StudentForm(instance=student, initial={'schedule': initial_schedule})

    return render(request, 'pages/edit_student.html', {
        'user_form': user_form,
        'student_form': student_form,
        'student': student,
    })

def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        #delete semua data yg konek ke itu user
        user = student.user
        user.delete() 
        
        messages.success(request, f'Student {user.name} has been successfully deleted.')
        return redirect('admin_students')
    else:
        return redirect('student_details', student_id=student_id)

def admin_teachers(request):
    sort = request.GET.get('sort', 'teacher')
    direction = request.GET.get('direction', 'asc')
    order_prefix = '' if direction == 'asc' else '-'

    search = request.GET.get('search', '')

    teachers = Teacher.objects.select_related('user')

    if search:
        teachers = teachers.filter(user__name__icontains=search)

    sort_fields = {
        'teacher': 'user__name',
        'points': 'point',
        'join_date': 'user__created_at',
    }
    sort_field = sort_fields.get(sort, 'user__name')
    teachers = teachers.order_by(f'{order_prefix}{sort_field}')

    return render(request, 'pages/admin_teachers.html', {
        'teachers': teachers,
        'sort': sort,
        'direction': direction,
        'search': search,
    })

def add_teacher(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        teacher_form = TeacherForm(request.POST, request.FILES)

        if user_form.is_valid() and teacher_form.is_valid(): #klo udh sesuai field baru dia return true
            user = user_form.save(commit=False)
            user.username = user.email
            user.set_password(user.password)
            user.role = 'teacher'
            user.status = 'active'
            user.save()

            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.save()

            messages.success(request, f"Teacher {user.name} successfully created!")
            return redirect('admin_teachers')
        else:
            messages.error(request, "Failed to save. Please enter the fields appropriately.") 
    else:
        user_form = UserForm()
        teacher_form = TeacherForm()

    return render(request, 'pages/add_teacher.html', {
        'user_form': user_form,
        'teacher_form': teacher_form,
    })



def teacher_details(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    summaries = Summary.objects.select_related(
        'material__course', 'student__user', 'session'
    ).filter(teacher=teacher).order_by('-dateCreated')[:5]

    for summary in summaries:
        next_material = Material.objects.filter(
            course=summary.material.course,
            order__gt=summary.material.order,
            isRemoved=False
        ).order_by('order').first()
        summary.next_material = next_material

    context = {
        'teacher': teacher,
        'summaries': summaries,
    }

    return render(request, 'pages/teacher_details.html', context)

def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    user = teacher.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher)

        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save(commit=False)
            #hash ulang password
            if 'password' in user_form.cleaned_data and user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()

            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.save()

            #schedule nya dibikin ulang
            Schedule.objects.filter(teacher=teacher).delete()

            messages.success(request, f"Teacher {user.name} edited successfully!")
            return redirect('admin_teachers')
        else:
            messages.error(request, "Failed to save. Please enter the fields appropriately.")
    else:
        user_form = UserForm(instance=user)
        teacher_form = TeacherForm(instance=teacher)

    return render(request, 'pages/edit_teacher.html', {
        'user_form': user_form,
        'teacher_form': teacher_form,
        'teacher': teacher,
    })

def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        #delete semua data yg konek ke itu user
        user = teacher.user
        user.delete() 
        
        messages.success(request, f'Teacher {user.name} has been successfully deleted.')
        return redirect('admin_teachers')
    else:
        return redirect('teacher_details', teacher_id=teacher_id)

def admin_courses(request):
    courses = Course.objects.filter(isRemoved=False).order_by('order')
    return render(request, 'pages/admin_courses.html', {'courses': courses})

def create_course(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name: #buat kasih tau klo sukses
            Course.objects.create(name=name)
            return redirect(reverse('admin_courses') + '?created=true')
    return redirect('admin_courses')

def course_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    sort = request.GET.get('sort', 'order')        
    direction = request.GET.get('direction', 'asc')

    allowed_sorts = ['order']
    if sort not in allowed_sorts:
        sort = 'order'

    order_prefix = '' if direction == 'asc' else '-'
    materials = Material.objects.filter(course=course, isRemoved=False).order_by(f'{order_prefix}{sort}')
    
    new_direction = 'desc' if direction == 'asc' else 'asc'


    return render(request, 'pages/course_list.html', {
        'course': course,
        'materials': materials,
        'sort': sort,
        'direction': direction,
        'new_direction': new_direction,
    })

def add_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course  # link material ke course
            material.save()
            messages.success(request, f"Material {material.name} successfully added!")
            return redirect('course_list', course_id=course.id)
        else:
            messages.error(request, "Failed to save. Please enter the fields appropriately.")
    else:
        form = MaterialForm()

    return render(request, 'pages/add_material.html', {'form': form, 'course': course})

def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('course_list', course_id=material.course.id)
    else:
        form = MaterialForm(instance=material)
        messages.error(request, "Failed to save. Please enter the fields appropriately.")
    
    messages.success(request, f"Material {material.name} successfully edited!")    
    return render(request, 'pages/edit_material.html', {'form': form, 'material': material})

def delete_material(request, material_id):
    if request.method == 'POST':
        material = get_object_or_404(Material, id=material_id)
        course_id = material.course.id
        material.delete()
        messages.success(request, f"Material {material.name} successfully deleted!")
        return redirect('course_list', course_id=course_id)
    return redirect('course_list', course_id=material.course.id)

def delete_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        messages.success(request, f"Course {course.name} successfully deleted!")
        return redirect('admin_courses')
    else:
        messages.error(request, "Failed to save. Please enter the fields appropriately.")
    return redirect('admin_courses')


def admin_payments(request):
    return render(request, 'pages/admin_payments.html')

def admin_payment_requests(request):
    return render(request, 'pages/admin_payment_requests.html')

def admin_certificates(request):
    return render(request, 'pages/admin_certificates.html')

def admin_pending_certificates(request):
    return render(request, 'pages/admin_pending_certificates.html')

def admin_unconfirmed_certificates(request):
    return render(request, 'pages/admin_unconfirmed_certificates.html')

def pending_summaries(request):
    return render(request, 'pages/pending_summaries.html')

def upload_teacher_image(request):
    if request.method == 'POST':
        image = request.FILES['teacherImage']
        teacher = Teacher.objects.get(user=request.user)
        teacher.teacherImage = image
        teacher.save()
        return redirect('dashboard_teacher')
    
def upload_student_image(request):
    if request.method == 'POST':
        image = request.FILES['studentImage']
        student = Student.objects.get(user=request.user)
        student.studentImage = image
        student.save()
        return redirect('dashboard_student')