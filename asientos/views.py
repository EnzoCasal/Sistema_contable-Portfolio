from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Asiento
from .serializers import AsientoSerializer
from .permissions import IsAdminOrContadorOrAyudanteOrAuditor
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime
from plan_cuentas.models import Cuenta
from .models import Movimiento

class LibroMayorView(APIView):
    def get(self, request):
        try:
            cuenta_id = request.query_params.get("cuenta_id")
            fecha_inicio = request.query_params.get("fecha_inicio")
            fecha_fin = request.query_params.get("fecha_fin")

            # Validaciones básicas
            if not cuenta_id or not fecha_inicio or not fecha_fin:
                return Response(
                    {"error": "Debe proporcionar cuenta_id, fecha_inicio y fecha_fin."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cuenta = Cuenta.objects.get(id=cuenta_id)
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            # Movimientos dentro del rango
            movimientos = Movimiento.objects.filter(
                cuenta=cuenta,
                fecha__range=[fecha_inicio, fecha_fin]
            ).order_by("fecha", "id")

            # Calcular saldo inicial (antes del rango)
            anteriores = Movimiento.objects.filter(
                cuenta=cuenta,
                fecha__lt=fecha_inicio
            ).aggregate(
                total_debe=Sum("debe"),
                total_haber=Sum("haber")
            )

            total_debe_ant = anteriores["total_debe"] or Decimal(0)
            total_haber_ant = anteriores["total_haber"] or Decimal(0)

            if cuenta.tipo in ["activo", "resultado_negativo"]:
                saldo_inicial = total_debe_ant - total_haber_ant
            else:
                saldo_inicial = total_haber_ant - total_debe_ant

            # Construir lista de movimientos con saldo progresivo
            saldo_actual = saldo_inicial
            lista_movs = []
            for mov in movimientos:
                if cuenta.tipo in ["activo", "resultado_negativo"]:
                    saldo_actual += mov.debe - mov.haber
                else:
                    saldo_actual += mov.haber - mov.debe

                lista_movs.append({
                    "fecha": mov.fecha,
                    "debe": float(mov.debe),
                    "haber": float(mov.haber),
                    "saldo": float(saldo_actual)
                })

            data = {
                "cuenta": {
                    "id": cuenta.id,
                    "nombre": cuenta.nombre,
                    "tipo": cuenta.tipo
                },
                "saldoInicial": float(saldo_inicial),
                "movimientos": lista_movs,
                "saldoFinal": float(saldo_actual)
            }

            return Response(data, status=status.HTTP_200_OK)

        except Cuenta.DoesNotExist:
            return Response({"error": "La cuenta no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AsientoViewSet(viewsets.ModelViewSet):
    queryset = Asiento.objects.all()
    serializer_class = AsientoSerializer

    @action(detail=False, methods=["get"], url_path="libro-mayor")
    def libro_mayor(self, request):
        cuenta_id = request.query_params.get("cuenta")
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        if not cuenta_id or not fecha_inicio or not fecha_fin:
            return Response(
                {"error": "Parámetros requeridos: cuenta, fecha_inicio, fecha_fin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cuenta = Cuenta.objects.get(id=cuenta_id)
        except Cuenta.DoesNotExist:
            return Response({"error": "La cuenta no existe"}, status=status.HTTP_404_NOT_FOUND)

        # Convertimos las fechas
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        # 🔹 Calcular saldo inicial (movimientos anteriores a la fecha_inicio)
        movimientos_anteriores = Movimiento.objects.filter(
            cuenta=cuenta,
            asiento__fecha__lt=fecha_inicio
        )

        saldo_inicial = Decimal(cuenta.saldo_actual)  # Si querés usar un saldo acumulado actual
        # O bien recalcularlo desde cero:
        saldo_inicial = Decimal(0)
        for mov in movimientos_anteriores:
            if cuenta.tipo in ["activo", "resultado_negativo"]:
                saldo_inicial += mov.debe - mov.haber
            else:
                saldo_inicial += mov.haber - mov.debe

        # 🔹 Obtener movimientos dentro del rango de fechas
        movimientos = Movimiento.objects.filter(
            cuenta=cuenta,
            asiento__fecha__range=[fecha_inicio, fecha_fin]
        ).select_related("asiento").order_by("asiento__fecha")

        movimientos_serializados = []
        saldo_actual = saldo_inicial

        for mov in movimientos:
            if cuenta.tipo in ["activo", "resultado_negativo"]:
                saldo_actual += mov.debe - mov.haber
            else:
                saldo_actual += mov.haber - mov.debe

            movimientos_serializados.append({
                "fecha": mov.asiento.fecha,
                "debe": mov.debe,
                "haber": mov.haber,
                "saldo": saldo_actual
            })

        response_data = {
            "cuenta": {
                "id": cuenta.id,
                "nombre": cuenta.nombre,
                "tipo": cuenta.tipo,
            },
            "saldoInicial": round(saldo_inicial, 2),
            "movimientos": movimientos_serializados,
            "saldoFinal": round(saldo_actual, 2),
        }

        return Response(response_data, status=status.HTTP_200_OK)