from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Cuenta
from .serializers import CuentaSerializer
from .permissions import IsAdminOrContadorOrAyudanteOrAuditor

class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrContadorOrAyudanteOrAuditor]

    # Búsqueda por código o nombre / ordenamiento
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "nombre"]
    ordering_fields = ["codigo", "nombre", "tipo"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtro opcional por padre: ?parent=<id>  |  root: ?parent=null
        parent_param = self.request.query_params.get("parent")

        if self.request.query_params.get("inactivas") == "true":
            qs = qs.filter(activo=False)
        else:
            qs = qs.filter(activo=True)
        
        if parent_param == "null":
            return qs.filter(parent__isnull=True)
        if parent_param:
            return qs.filter(parent_id=parent_param)
        return qs
