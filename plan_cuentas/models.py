from django.db import models
from django.db.models import Sum
from decimal import Decimal


class Cuenta(models.Model):
    TIPO_CHOICES = [
        ("activo", "Activo"),
        ("pasivo", "Pasivo"),
        ("patrimonio", "Patrimonio"),
        ("ingreso", "Ingreso"),
        ("gasto", "Gasto"),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=[("activo", "Activo"), ("pasivo", "Pasivo")])
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def saldo_actual(self):
        from plan_cuentas.models import Movimiento
        totales = Movimiento.objects.filter(cuenta=self).aggregate(
            total_debe=Sum("debe"),
            total_haber=Sum("haber")
        )
        total_debe = totales["total_debe"] or Decimal("0")
        total_haber = totales["total_haber"] or Decimal("0")
        return self.saldo_inicial + total_debe - total_haber

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Genera el código automáticamente si no existe
        if not self.codigo:
            if self.parent:
                # Hijas: usar el código del padre + número secuencial
                siblings = Cuenta.objects.filter(parent=self.parent)
                next_number = siblings.count() + 1
                self.codigo = f"{self.parent.codigo}.{next_number}"
            else:
                # Cuentas raíz: número secuencial
                root_count = Cuenta.objects.filter(parent__isnull=True).count() + 1
                self.codigo = str(root_count)
        super().save(*args, **kwargs)

class Movimiento(models.Model):
    cuenta = models.ForeignKey("plan_cuentas.Cuenta", related_name="movimientos", on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.fecha} - {self.cuenta.nombre} ({self.debe}/{self.haber})"