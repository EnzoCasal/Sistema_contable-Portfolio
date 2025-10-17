# asientos/serializers.py
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
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
        fields = [
            "id",
            "fecha",
            "descripcion",
            "movimientos",
            "total_debe",
            "total_haber",
            "es_balanceado",
            "usuario",
        ]
        read_only_fields = ["total_debe", "total_haber", "es_balanceado", "usuario"]

    # --- Validaciones ---
    def validate(self, data):
        movimientos = data.get("movimientos", [])
        total_debe = sum(Decimal(str(m.get("debe", 0))) for m in movimientos)
        total_haber = sum(Decimal(str(m.get("haber", 0))) for m in movimientos)

        if total_debe != total_haber:
            raise serializers.ValidationError(
                f"El asiento no está balanceado: total debe = {total_debe}, total haber = {total_haber}."
            )

        # 🔹 Validar saldo negativo solo para tipos que no pueden tenerlo
        for mov in movimientos:
            cuenta = mov["cuenta"]
            cuenta_obj = Cuenta.objects.get(pk=cuenta.id)

            if cuenta_obj.tipo in ["activo", "resultado_positivo"]:
                if cuenta_obj.tipo == "activo" or cuenta_obj.tipo == "resultado_positivo":
                    if cuenta_obj.tipo in ["activo", "resultado_negativo"]:
                        nuevo_saldo = cuenta_obj.saldo_actual + (mov["debe"] - mov["haber"])
                    else:
                        nuevo_saldo = cuenta_obj.saldo_actual + (mov["haber"] - mov["debe"])

                    if nuevo_saldo < 0:
                        raise serializers.ValidationError(
                            f"La cuenta '{cuenta_obj.nombre}' no puede tener saldo negativo (intenta quedar en {nuevo_saldo})."
                        )

        return data

    # --- Crear asiento ---
    def create(self, validated_data):
        movimientos_data = validated_data.pop("movimientos")

        with transaction.atomic():
            asiento = Asiento.objects.create(
                usuario=self.context["request"].user, **validated_data
            )

            for mov_data in movimientos_data:
                mov = Movimiento.objects.create(asiento=asiento, **mov_data)
                self._actualizar_saldo_cuenta(mov)

        return asiento

    # --- Actualizar asiento ---
    def update(self, instance, validated_data):
        movimientos_data = validated_data.pop("movimientos", None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if movimientos_data is not None:
                for mov in instance.movimientos.all():
                    self._revertir_saldo_cuenta(mov)
                instance.movimientos.all().delete()

                for mov_data in movimientos_data:
                    mov = Movimiento.objects.create(asiento=instance, **mov_data)
                    self._actualizar_saldo_cuenta(mov)

        return instance

    # --- Actualizar saldo ---
    def _actualizar_saldo_cuenta(self, movimiento):
        cuenta = movimiento.cuenta
        if cuenta.tipo in ["activo", "resultado_negativo"]:
            cuenta.saldo_actual += movimiento.debe - movimiento.haber
        else:
            cuenta.saldo_actual += movimiento.haber - movimiento.debe
        cuenta.save()

    # --- Revertir saldo ---
    def _revertir_saldo_cuenta(self, movimiento):
        cuenta = movimiento.cuenta
        if cuenta.tipo in ["activo", "resultado_negativo"]:
            cuenta.saldo_actual -= movimiento.debe - movimiento.haber
        else:
            cuenta.saldo_actual -= movimiento.haber - movimiento.debe
        cuenta.save()
