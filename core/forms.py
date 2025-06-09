# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.widgets import DateInput
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'name',
            'gender',
            'phone',
            'role',
            'status',
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'name',
            'gender',
            'phone',
            'role',
            'status',
        )

DAYS_OF_WEEK = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'enter password'}),
        required=True
    )

    # created_at = forms.DateField(
    #     widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    #     input_formats=['%Y-%m-%d'],
    #     required=True
    # )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password'] #taro created_at juga klo mau
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'enter name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'enter phone no.'}),
            
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time','class': 'form-control'}),
        }

class StudentForm(forms.ModelForm):

    schedule = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True  
    )

    studentImage = forms.ImageField(required=False)
    grade = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'grade:'}),
    )

    class Meta:
        model = Student
        fields = ['studentImage', 'grade']

class TeacherForm(forms.ModelForm):
    teacherImage = forms.ImageField(required=False)

    class Meta:
        model = Teacher
        fields = ['teacherImage']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course name'}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['order','name', 'description', 'link']