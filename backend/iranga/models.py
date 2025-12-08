from django.db import models

class Iranga(models.Model):
    id_iranga = models.AutoField(primary_key=True)
    Pavadinimas = models.CharField(max_length=255)
    Tipas = models.IntegerField()
    Bukle = models.CharField(max_length=255)
    Vieta = models.CharField(max_length=255)
    Verte = models.DecimalField(max_digits=10, decimal_places=2)
    Gamintojas = models.CharField(max_length=255)
    Pagaminimo_data = models.DateField()
    Technine_apziura = models.DateField()

    class Meta:
        db_table = "iranga"

    def __str__(self):
        return self.Pavadinimas