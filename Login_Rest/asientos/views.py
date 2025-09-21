from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Asiento
from .serializers import AsientoSerializer
from .permissions import IsAdminOrContadorOrAyudanteOrAuditor

class AsientoViewSet(viewsets.ModelViewSet):
    queryset = Asiento.objects.all()
    serializer_class = AsientoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrContadorOrAyudanteOrAuditor]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context