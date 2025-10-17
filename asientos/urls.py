from rest_framework.routers import DefaultRouter
from .views import AsientoViewSet

router = DefaultRouter()
router.register(r"asientos", AsientoViewSet, basename="asiento")

urlpatterns = router.urls
