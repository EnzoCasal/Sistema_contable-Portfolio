from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import DashboardAPIView, MyTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login con JWT
    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint privado
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    #  Plan de cuentas
    path("api/", include("plan_cuentas.urls")),

    path("api/", include("accounts.urls")),

    path("api/", include("asientos.urls")),
]
