from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, GoogleLoginView

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
]
