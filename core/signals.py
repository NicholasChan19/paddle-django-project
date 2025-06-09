from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.apps import apps

User = apps.get_model('core', 'User')
Teacher = apps.get_model('core', 'Teacher')
Student = apps.get_model('core', 'Student')
Summary = apps.get_model('core', 'Summary')


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'teacher':
            Teacher.objects.create(user=instance)
            print(f"✅ Teacher created for {instance.name}")
        elif instance.role == 'student':
            Student.objects.create(user=instance)
            print(f"✅ Student created for {instance.name}")

@receiver(post_save, sender=Summary)
def handle_summary_created(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        if student.remainingSession > 0:
            student.remainingSession -= 1
            student.sessionDone += 1
            student.save()
            print(f"✅ Session deducted for {student.user.name}")
        else:
            print(f"⚠️ No remaining session for {student.user.name}")