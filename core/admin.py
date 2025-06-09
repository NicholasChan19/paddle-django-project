from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'name', 'role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informasi Pribadi', {'fields': ('name', 'email', 'gender', 'phone', 'role', 'status')}),
        ('Hak Akses', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Tanggal Penting', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'name', 'role'),
        }),
    )
    search_fields = ('username', 'email', 'name')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Summary)
admin.site.register(Certificate)
admin.site.register(Payment)
admin.site.register(Notification)
admin.site.register(Session)
admin.site.register(Schedule)
admin.site.register(Material)
admin.site.register(Leaderboard)