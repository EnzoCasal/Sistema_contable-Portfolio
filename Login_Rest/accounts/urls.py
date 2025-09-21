# usuarios/urls.py
from rest_framework.routers import DefaultRouter
from .views import UserAdminViewSet

router = DefaultRouter()
router.register(r'usuarios', UserAdminViewSet, basename="usuarios")

urlpatterns = router.urls
