from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from datetime import datetime, timedelta
from .models import (
    User, School, Department, Program, Class, Faculty, 
    Student, Course, Assignment, AssignmentComment,
    Attendance, Grade, Note, Announcement, AnnouncementComment
)
from .serializers import (
    UserSerializer, SchoolSerializer, DepartmentSerializer,
    ProgramSerializer, ClassSerializer, FacultySerializer,
    StudentSerializer, CourseSerializer, AssignmentSerializer,
    AssignmentCommentSerializer, AttendanceSerializer,
    GradeSerializer, NoteSerializer, AnnouncementSerializer,
    AnnouncementCommentSerializer
)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user_type = request.data.get("user_type")  # user_type should come from the frontend

        # Validate if email and password are provided
        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Use the custom manager to authenticate using email
        User = get_user_model()

        # Authenticate the user using email and password
        user = User.objects.authenticate(request, email=email, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Now check if the user_type matches
        if user.user_type != user_type:
            return Response({"detail": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        # Create JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_type': user.user_type,  # Return the user type in the response
        })



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def upload_students(self, request):
        """
        Upload students via CSV file
        """
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        program_id = request.data.get('program_id')
        if not program_id:
            return Response({'error': 'Program ID is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded_file))
        
        created_students = []
        for row in csv_data:
            try:
                # Create user
                user = User.objects.create_user(
                    username=row['registration_number'],
                    email=row['email'],
                    password=row['password'],
                    first_name=row['name'],
                    user_type='student'
                )
                
                # Create student profile
                student = Student.objects.create(
                    user=user,
                    registration_number=row['registration_number'],
                    program_id=program_id,
                    current_semester=1
                )
                
                created_students.append(student)
                
            except Exception as e:
                return Response({'error': f'Error creating student: {str(e)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Successfully created {len(created_students)} students'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def start_new_session(self, request):
        """
        Increment semester for all active students
        """
        try:
            Student.objects.filter(user__is_active=True).update(
                current_semester=models.F('current_semester') + 1
            )
            return Response({'message': 'Successfully started new academic session'})
        except Exception as e:
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'faculty':
            return Faculty.objects.filter(user=self.request.user)
        return super().get_queryset()
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Get courses taught by faculty
        """
        faculty = self.get_object()
        courses = Course.objects.filter(faculty=faculty)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'student':
            return Student.objects.filter(user=self.request.user)
        return super().get_queryset()
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Get courses for student's current semester
        """
        student = self.get_object()
        courses = Course.objects.filter(
            class_group__program=student.program,
            class_group__semester=student.current_semester
        )
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            student = Student.objects.get(user=user)
            return Assignment.objects.filter(
                course__class_group__program=student.program,
                course__class_group__semester=student.current_semester
            )
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Assignment.objects.filter(course__faculty=faculty)
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        assignment = self.get_object()
        serializer = AssignmentCommentSerializer(data={
            'assignment': assignment.id,
            'user': request.user.id,
            'comment': request.data.get('comment')
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        assignment = self.get_object()
        comments = AssignmentComment.objects.filter(assignment=assignment)
        serializer = AssignmentCommentSerializer(comments, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return Attendance.objects.filter(student__user=user)
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Attendance.objects.filter(course__faculty=faculty)
        return super().get_queryset()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create attendance records for a class
        """
        course_id = request.data.get('course_id')
        date = request.data.get('date')
        attendance_data = request.data.get('attendance', [])

        try:
            course = Course.objects.get(id=course_id)
            if request.user != course.faculty.user:
                return Response(
                    {'error': 'Not authorized'}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            attendance_records = []
            for record in attendance_data:
                attendance_records.append(
                    Attendance(
                        course_id=course_id,
                        student_id=record['student_id'],
                        date=date,
                        is_present=record['is_present']
                    )
                )

            Attendance.objects.bulk_create(attendance_records)
            return Response({'message': 'Attendance recorded successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def student_report(self, request):
        """
        Get attendance report for a student
        """
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')
        time_period = request.query_params.get('period', 'all')  # 'month' or 'all'

        queryset = self.get_queryset().filter(
            student_id=student_id,
            course_id=course_id
        )

        if time_period == 'month':
            start_date = datetime.now() - timedelta(days=30)
            queryset = queryset.filter(date__gte=start_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return Grade.objects.filter(student__user=user)
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Grade.objects.filter(course__faculty=faculty)
        return super().get_queryset()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create grades for a course
        """
        course_id = request.data.get('course_id')
        grade_data = request.data.get('grades', [])

        try:
            course = Course.objects.get(id=course_id)
            if request.user != course.faculty.user:
                return Response(
                    {'error': 'Not authorized'}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            grades = []
            for grade in grade_data:
                grades.append(
                    Grade(
                        course_id=course_id,
                        student_id=grade['student_id'],
                        title=grade['title'],
                        marks_obtained=grade['marks_obtained'],
                        total_marks=grade['total_marks'],
                        remarks=grade.get('remarks', ''),
                        date=datetime.now().date()
                    )
                )

            Grade.objects.bulk_create(grades)
            return Response({'message': 'Grades recorded successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            student = Student.objects.get(user=user)
            return Note.objects.filter(
                course__class_group__program=student.program,
                course__class_group__semester=student.current_semester
            )
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Note.objects.filter(course__faculty=faculty)
        return super().get_queryset()

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            student = Student.objects.get(user=user)
            return Announcement.objects.filter(
                course__class_group__program=student.program,
                course__class_group__semester=student.current_semester
            )
        elif user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Announcement.objects.filter(course__faculty=faculty)
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        announcement = self.get_object()
        serializer = AnnouncementCommentSerializer(data={
            'announcement': announcement.id,
            'user': request.user.id,
            'comment': request.data.get('comment')
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        announcement = self.get_object()
        comments = AnnouncementComment.objects.filter(announcement=announcement)
        serializer = AnnouncementCommentSerializer(comments, many=True)
        return Response(serializer.data)