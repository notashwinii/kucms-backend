from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, School, Department, Program, Class, Faculty, 
    Student, Course, Assignment, AssignmentComment,
    Attendance, Grade, Note, Announcement, AnnouncementComment
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Display email instead of username
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active')
    
    # Filter by user_type, is_active, and is_staff
    list_filter = ('user_type', 'is_active', 'is_staff')
    
    # Custom fieldsets for admin view - use email instead of username
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Email and password
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields to show when adding a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    # Make search fields to include email, first_name, and last_name
    search_fields = ('email', 'first_name', 'last_name')
    
    # Default ordering by email
    ordering = ('email',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('id','name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name','school')
    list_filter = ('name','school')
    search_fields = ('id','name')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department__school', 'department')
    search_fields = ('name', 'department')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('program', 'semester', 'academic_year')
    list_filter = ('program', 'semester', 'academic_year')
    search_fields = ('program__name',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'faculty_type')
    list_filter = ('department', 'faculty_type')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'user', 'program', 'current_semester')
    list_filter = ('program', 'current_semester')
    search_fields = ('registration_number', 'user__username', 'user__first_name', 'user__last_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'class_group', 'faculty')
    list_filter = ('class_group__program', 'faculty')
    search_fields = ('code', 'name')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')

@admin.register(AssignmentComment)
class AssignmentCommentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment', 'user__username')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'date', 'is_present')
    list_filter = ('course', 'date', 'is_present')
    search_fields = ('student__registration_number',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'title', 'marks_obtained', 'total_marks', 'date')
    list_filter = ('course', 'date')
    search_fields = ('student__registration_number', 'title')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')
    list_filter = ('course', 'uploaded_at')
    search_fields = ('title',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content')

@admin.register(AnnouncementComment)
class AnnouncementCommentAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment', 'user__username')