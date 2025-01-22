from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

    def authenticate(self, request, email=None, password=None):
        """
        Authenticate using email instead of username.
        """
        try:
            user = self.get(email=email)
            if user.check_password(password):
                return user
            else:
                return None
        except self.model.DoesNotExist:
            return None

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(unique=True)  # Ensure email is unique
    
    # Set the email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # You may want to include username if you still need it for other purposes

    def __str__(self):
        return f"{self.email} - {self.user_type}"



    
class School(models.Model):
    """
    School entity
    """
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Department(models.Model):
    """
    Department within a school
    """
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}"

class Program(models.Model):
    """
    Academic program within a department
    """
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Class(models.Model):
    """
    Class representing program + semester combination
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ('program', 'semester', 'academic_year')
    
    def __str__(self):
        return f"{self.program.name} - Semester {self.semester}"

class Faculty(models.Model):
    """
    Additional faculty information
    """
    FACULTY_TYPES = (
        ('lecturer', 'Lecturer'),
        ('assistant arofessor', 'Assistant Professor'),
        ('professor', 'Professor'),
    )
     
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    faculty_type = models.CharField(max_length=50,choices=FACULTY_TYPES)  
   
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"

class Student(models.Model):
    """
    Additional student information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    current_semester = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name()}"

class Course(models.Model):
    """
    Course taught in a class
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Assignment(models.Model):
    """
    Assignment model for courses
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(
        upload_to='assignments/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        null=True, blank=True
    )
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"

class AssignmentComment(models.Model):
    """
    Comments on assignments
    """
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.assignment.title}"

class Attendance(models.Model):
    """
    Student attendance records
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('course', 'student', 'date')
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.date}"

class Grade(models.Model):
    """
    Student grades
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # e.g., "Midterm", "Quiz 1"
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    date = models.DateField()
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.title}"

class Note(models.Model):
    """
    Course notes/materials
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='notes/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'ppt', 'pptx'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"

class Announcement(models.Model):
    """
    Course announcements
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"

class AnnouncementComment(models.Model):
    """
    Comments on announcements
    """
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.announcement.title}"