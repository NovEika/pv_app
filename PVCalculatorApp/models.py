from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import Group, Permission

# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class MyUser(AbstractUser, PermissionsMixin):
    username = None
    GROUP_LEADER = 'group_leader'
    ENGINEER = 'engineer'

    ROLE_CHOICES = [
        (GROUP_LEADER, 'Group Leader'),
        (ENGINEER, 'Engineer'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ENGINEER)

    group_leader = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='engineers', null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True,
                                    help_text = 'The groups this user belongs to.')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True,
                                              help_text = 'Specific permissions for this user.')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


#třída střídače pro zadání optimáního, maximálního a minimálního napětí střídače, a maximálního počtu mpp trackerů
class Inverter(models.Model):
    name = models.CharField(max_length=32)
    opt_input_voltage = models.FloatField()
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
    project_name = models.CharField(max_length=64, default="Unnamed Project")


class Solution(models.Model):
    # name = models.CharField(max_length=32)
    nDCmaxINV = models.IntegerField()
    nDCminINV = models.IntegerField()
    nDCoptINV = models.IntegerField()
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='solutions')

class SolutionProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, null=True)

class StringPair(models.Model):
    LOW_MPPT = 'low_mppt'

    RESULT_CHOICES = [
        (LOW_MPPT, 'low_mppt'),
    ]

    string1 = models.IntegerField()
    string2 = models.IntegerField()
    result = models.CharField(max_length=50, choices=RESULT_CHOICES, default=LOW_MPPT)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='string_pairs', default=None,
                                 null=True, blank=True)