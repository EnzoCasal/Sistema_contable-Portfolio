from rest_framework import serializers
from .models import Cuenta

class CuentaSerializer(serializers.ModelSerializer):
    saldo_actual = serializers.ReadOnlyField()
    codigo = serializers.ReadOnlyField()

    class Meta:
        model = Cuenta
        fields = ["id", "codigo", "nombre", "tipo", "saldo_inicial", "saldo_actual", "parent"]

    def validate(self, attrs):
        # (Opcional) Evitar que una cuenta sea su propio padre al actualizar
        parent = attrs.get("parent")
        if self.instance and parent and parent.id == self.instance.id:
            raise serializers.ValidationError("Una cuenta no puede ser su propio padre.")
        return attrs

    def get_saldo_actual(self, obj):
        # saldo_actual se calcula dinámicamente
        return obj.saldo_actual()