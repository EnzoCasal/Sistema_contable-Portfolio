from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework import viewsets
from .models import User
from rest_framework.permissions import BasePermission
from .permissions import IsAdminRole
from .serializers import UserAdminSerializer

# Endpoint protegido
class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hola {request.user.username}, estás autenticado!"
        })
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class UserAdminViewSet(viewsets.ModelViewSet):
    """
    Endpoint para admins: listar, crear, actualizar y eliminar usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminRole]