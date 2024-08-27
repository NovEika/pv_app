from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# class MyUser(AbstractUser):
#     position = models.CharField(max_length=20, blank=True, null=True)

#oneToMany group leader --> projektant???

#třída střídače pro zadání optimáního, maximálního a minimálního napětí střídače, a maximálního počtu mpp trackerů
class Inverter(models.Model):
    name = models.CharField(max_length=32)
    optimal_input_voltage = models.FloatField()
    max_input_voltage = models.FloatField()
    min_input_voltage = models.FloatField()
    max_mppt_count = models.IntegerField()

#třída panelu
class Panel(models.Model):
    name = models.CharField(max_length=32)
    #napětí FV modulu naprázdno
    UocMOD_volt = models.FloatField()
    #teplotní koeficient modulu
    TMOD_percent = models.FloatField()
    #napětí FV modulu při max výkonu
    UmmpMOD_volt = models.FloatField()
    #teplotní koeficient modulu Pmax
    TMOD_pMax_percent = models.FloatField()
    #proud nakrátko
    ISC_amper = models.FloatField()
    #teplotní koeficient proudu nakrátko
    TMOD_short_percent = models.FloatField()

#název projektu nebo lokace
class Project(models.Model):
    name = models.CharField(max_length=64)


class Solution(models.Model):
    name = models.CharField(max_length=32)
    #list panelů????
    nDCmaxINV = models.IntegerField()
    nDCminINV = models.IntegerField()
    nDCoptINV = models.IntegerField()

class SolutionProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)