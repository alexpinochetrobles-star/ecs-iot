from django.db import models


class LecturaPozo(models.Model):
    """Lecturas normativas del pozo (NCh 777 / DGA)."""
    fecha_hora         = models.DateTimeField(auto_now_add=True, db_index=True)
    nivel_estatico_m   = models.FloatField(verbose_name="Nivel Estático (m)")
    nivel_dinamico_m   = models.FloatField(verbose_name="Nivel Dinámico (m)")
    caudal_lps         = models.FloatField(verbose_name="Caudal (L/s)")
    bomba_encendida    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = "Lectura de Pozo"
        verbose_name_plural = "Lecturas de Pozo"
        permissions = [
            ("can_control_bomba", "Puede encender/apagar la bomba del pozo"),
        ]

    def __str__(self):
        return f"{self.fecha_hora:%Y-%m-%d %H:%M:%S} | NE={self.nivel_estatico_m}m ND={self.nivel_dinamico_m}m Q={self.caudal_lps}L/s"


class EventoBomba(models.Model):
    """Auditoría de comandos de la bomba (trazabilidad)."""
    TIPO_CHOICES = [
        ('ENCENDIDO',      'Encendido manual'),
        ('APAGADO',        'Apagado manual'),
        ('AUTO_APAGADO',   'Apagado automático por alarma'),
        ('BLOQUEO',        'Intento bloqueado'),
    ]
    fecha_hora  = models.DateTimeField(auto_now_add=True, db_index=True)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    usuario     = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField()

    class Meta:
        ordering = ['-fecha_hora']