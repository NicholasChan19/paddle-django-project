from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('quit', 'Quit'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='male')
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'  
    REQUIRED_FIELDS = ['email', 'name']  

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacherImage = models.ImageField(upload_to='profile_pics/', default='default_teacher.png')
    badge = models.CharField(max_length=20, default='')
    point = models.IntegerField(default=0)
    allTimeTopOne = models.IntegerField(default=0)
    allTimeTopThree = models.IntegerField(default=0)
    summaryDone = models.IntegerField(default=0)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    studentImage = models.ImageField(upload_to='student_pics/', default='student_pics/default_students/default_student.png')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True)
    paymentPending = models.IntegerField(default=0)
    remainingSession = models.IntegerField(default=0)
    sessionDone = models.IntegerField(default=0)
    grade = models.CharField(max_length=100, default='No grade')


class Schedule(models.Model):
    SCHEDULE_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='Monday')


class Course(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    isRemoved = models.BooleanField(default=False)


class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    link = models.CharField(max_length=100, default='')
    isRemoved = models.BooleanField(default=False)


class Session(models.Model):
    date = models.DateField()
    time = models.TimeField()


class Summary(models.Model):
    RATING_CHOICES = [(1, '1'), (2, '2'), (3, '3')]

    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, default=' ', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, default=' ', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, default=' ', on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)
    mastery = models.IntegerField(choices=RATING_CHOICES, default=1)
    attitude = models.IntegerField(choices=RATING_CHOICES, default=1)
    improvement = models.IntegerField(choices=RATING_CHOICES, default=1)
    summary = models.TextField(default=' ', blank=True)
    notes = models.CharField(max_length=255, default=' ', blank=True)
    summaryImage = models.ImageField(upload_to='summary_images/', default='summary_images/default.jpg')
    certificateReminder = models.BooleanField(default=False)
    certificateCreated = models.BooleanField(default=False)
    summaryCreated = models.BooleanField(default=False)



class Certificate(models.Model):
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)
    mastery = models.IntegerField(choices=Summary.RATING_CHOICES, default=1)
    attitude = models.IntegerField(choices=Summary.RATING_CHOICES, default=1)
    improvement = models.IntegerField(choices=Summary.RATING_CHOICES, default=1)
    description = models.TextField(default='')
    certificateImage = models.ImageField(upload_to='certificate_images/', default='certificate_images/default.jpg')
    signatureLogo = models.ImageField(upload_to='signatures/', default='signatures/default.jpg')
    projectFile = models.FileField(upload_to='project_files/', default='project_files/default.zip')  # bisa juga pakai FileField
    projectLink = models.CharField(max_length=255, default='')
    isAccepted = models.BooleanField(default=False)
    adminNotes = models.CharField(max_length=255, default='')


class Payment(models.Model):
    STATUS_CHOICES = [
        (0, 'Requested'),
        (1, 'Issued'),
        (2, 'Pending Confirmation'),
        (3, 'Paid'),
        (4, 'Overdue'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    sessionAmount = models.IntegerField(default=0)
    createdAt = models.DateField(auto_now_add=True)
    chargeAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    paymentCreated = models.BooleanField(default=False)
    dueDate = models.DateField(null=True, blank=True)
    paymentImage = models.ImageField(upload_to='payment_proofs/', null=True, blank=True, default='payment_proofs/default.jpg')
    paidConfirmedDate = models.DateField(null=True, blank=True)


class Notification(models.Model):
    TYPE_CHOICES = [
        ('sessionCreated', 'Session Created'),
        ('sessionReminder', 'Session Reminder'),
        ('noSessionLeft', 'No Session Left'),
        ('addSessionRequest', 'Add Session Request'),
        ('issuePayment', 'Issue Payment'),
        ('incomingPayment', 'Incoming Payment'),
        ('paymentOverdue', 'Payment Overdue'),
        ('paymentConfirmed', 'Payment Confirmed'),
        ('paymentDeclined', 'Payment Declined'),
        ('certificateIssued', 'Certificate Issued'),
        ('certificateConfirmed', 'Certificate Confirmed'),
        ('certificateDeclined', 'Certificate Declined'),
        ('newCertificate', 'New Certificate'),
        ('remindSummary', 'Remind Summary'),
        ('remindCertificate', 'Remind Certificate'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField(default='')
    isRead = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)


class Leaderboard(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    weekStart = models.DateField()
    weekEnd = models.DateField()
    rank = models.IntegerField(default=0)
    basePoints = models.IntegerField(default=0)
    bonusPoints = models.IntegerField(default=0)
    totalPoints = models.IntegerField(default=0)

    class Meta:
        unique_together = ('teacher', 'weekStart')