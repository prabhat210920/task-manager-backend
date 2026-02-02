from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
import os

from .models import Goal, DailyLog
from .serializers import GoalSerializer, DailyLogSerializer

User = get_user_model()

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Verify Google access token and return JWT tokens
        Expects: { "access_token": "..." }
        """
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response(
                {'error': 'access_token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify the token with Google
            # For access_token verification, we need to call Google's tokeninfo endpoint
            import requests as http_requests
            response = http_requests.get(
                'https://www.googleapis.com/oauth2/v3/tokeninfo',
                params={'access_token': access_token}
            )
            
            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid access token'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_info = response.json()
            email = user_info.get('email')
            
            if not email:
                return Response(
                    {'error': 'Email not found in token'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                }
            )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'pk': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def log_progress(self, request, pk=None):
        goal = self.get_object()
        serializer = DailyLogSerializer(data=request.data)
        
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            log = serializer.save(goal=goal)
            
            # Update goal total
            goal.units_completed += amount
            goal.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
