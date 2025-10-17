from rest_framework import serializers
from .models import Cuenta

class CuentaSerializer(serializers.ModelSerializer):
    codigo = serializers.ReadOnlyField()

    class Meta:
        model = Cuenta
        fields = ["id", "codigo", "nombre", "tipo", "saldo_actual", "parent", "activo"]

    def validate(self, attrs):
        # (Opcional) Evitar que una cuenta sea su propio padre al actualizar
        parent = attrs.get("parent")
        if self.instance and parent and parent.id == self.instance.id:
            raise serializers.ValidationError("Una cuenta no puede ser su propio padre.")
        return attrs