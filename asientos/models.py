from django.db import models
from plan_cuentas.models import Cuenta 
from django.conf import settings

class Asiento(models.Model):
    fecha = models.DateField()
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asientos_creados"
    )

    def __str__(self):
        return f"Asiento {self.id} - {self.fecha}"

    def total_debe(self):
        return sum(mov.debe for mov in self.movimientos.all())

    def total_haber(self):
        return sum(mov.haber for mov in self.movimientos.all())

    def es_balanceado(self):
        return self.total_debe() == self.total_haber()


class Movimiento(models.Model):
    asiento = models.ForeignKey(
        Asiento, related_name="movimientos", on_delete=models.CASCADE
    )
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT)
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Mov {self.id} - {self.cuenta.nombre} (Debe: {self.debe}, Haber: {self.haber})"
