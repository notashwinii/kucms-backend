from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import UserLoginForm
from .models import CustomUser

class LoginView(APIView):
    def post(self, request):
        form = UserLoginForm(request.data)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Check user type and authenticate accordingly
            try:
                user = CustomUser.objects.get(email=email)
                
                if user.is_student:
                    student = authenticate(request, username=user.email, password=password)
                elif user.is_faculty:
                    faculty = authenticate(request, username=user.email, password=password)
                elif user.is_admin:
                    admin = authenticate(request, username=user.email, password=password)
                
                if student or faculty or admin:
                    login(request, user)
                    return Response({"message": "Login successful", "user_type": user.USER_TYPES[user.is_student] if user.is_student else (user.is_faculty and 'F' or 'A')})
                else:
                    return Response({"error": "Invalid credentials"}, status=401)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response(form.errors, status=400)
