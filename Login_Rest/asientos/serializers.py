# asientos/serializers.py
from rest_framework import serializers
from decimal import Decimal
from .models import Asiento, Movimiento
from plan_cuentas.models import Cuenta

class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = ["id", "cuenta", "debe", "haber"]

class AsientoSerializer(serializers.ModelSerializer):
    movimientos = MovimientoSerializer(many=True)

    class Meta:
        model = Asiento
        fields = ["id", "fecha", "descripcion", "movimientos",
                  "total_debe", "total_haber", "es_balanceado", "usuario"]
        read_only_fields = ["total_debe", "total_haber", "es_balanceado", "usuario"]

    def validate(self, data):
        movimientos = data.get("movimientos", [])
        total_debe = sum(Decimal(str(m.get("debe", 0))) for m in movimientos)
        total_haber = sum(Decimal(str(m.get("haber", 0))) for m in movimientos)

        if total_debe != total_haber:
            raise serializers.ValidationError(
                f"El asiento no está balanceado: total debe = {total_debe}, total haber = {total_haber}."
            )
        return data

    def create(self, validated_data):
        movimientos_data = validated_data.pop("movimientos")
        asiento = Asiento.objects.create(usuario=self.context["request"].user, **validated_data)
        
        for mov_data in movimientos_data:
            mov = Movimiento.objects.create(asiento=asiento, **mov_data)
            self._actualizar_saldo_cuenta(mov)

        return asiento

    def update(self, instance, validated_data):
        movimientos_data = validated_data.pop("movimientos", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if movimientos_data is not None:
            # Revertimos saldos de movimientos antiguos
            for mov in instance.movimientos.all():
                self._revertir_saldo_cuenta(mov)
            instance.movimientos.all().delete()
            
            for mov_data in movimientos_data:
                mov = Movimiento.objects.create(asiento=instance, **mov_data)
                self._actualizar_saldo_cuenta(mov)

        return instance

    def _actualizar_saldo_cuenta(self, movimiento):
        cuenta = movimiento.cuenta
        if cuenta.tipo in ["activo", "resultado_negativo"]:
            cuenta.saldo_actual += movimiento.debe - movimiento.haber
        elif cuenta.tipo in ["pasivo", "patrimonio", "resultado_positivo"]:
            cuenta.saldo_actual += movimiento.haber - movimiento.debe
        cuenta.save()

    def _revertir_saldo_cuenta(self, movimiento):
        cuenta = movimiento.cuenta
        if cuenta.tipo in ["activo", "resultado_negativo"]:
            cuenta.saldo_actual -= movimiento.debe - movimiento.haber
        elif cuenta.tipo in ["pasivo", "patrimonio", "resultado_positivo"]:
            cuenta.saldo_actual -= movimiento.haber - movimiento.debe
        cuenta.save()
