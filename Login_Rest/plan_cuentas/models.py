from django.db import models

class Cuenta(models.Model):
    TIPO_CHOICES = [
        ("activo", "Activo"),
        ("pasivo", "Pasivo"),
        ("patrimonio", "Patrimonio"),
        ("resultado_positivo", "Resultado positivo"),
        ("resultado_negativo", "Resultado negativo"),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Genera el código automáticamente si no existe
        if not self.codigo:
            if self.parent:
                siblings = Cuenta.objects.filter(parent=self.parent)
                self.codigo = f"{self.parent.codigo}.{siblings.count() + 1}"
            else:
                root_count = Cuenta.objects.filter(parent__isnull=True).count() + 1
                self.codigo = str(root_count)
        super().save(*args, **kwargs)
