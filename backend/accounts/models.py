from django.db import models
from django.db import models

class Naudotojas(models.Model):
    PAREIGOS = [
        (1, "Klientas"),
        (2, "Darbuotojas"),
    ]

    id_Naudotojas = models.AutoField(primary_key=True)
    Vardas = models.CharField(max_length=255)
    Pavarde = models.CharField(max_length=255)
    El_pastas = models.CharField(max_length=255, unique=True)
    Slaptazodis = models.CharField(max_length=255)
    Pareigos = models.IntegerField(choices=PAREIGOS)
    Saskaitos_numeris = models.CharField(max_length=34)

    class Meta:
        db_table = "naudotojas"
        managed = False  # lentele jau sukurta MySQL, Django jos nekurs

    def __str__(self):
        return f"{self.Vardas} {self.Pavarde}"
# Create your models here.
