from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

router.register(r'assignments', views.AssignmentViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'announcements', views.AnnouncementViewSet)

urlpatterns = [
     # Token obtain and refresh views
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Your custom login view if you have any custom logic
    path('api/login/', LoginView.as_view(), name='login'),
]