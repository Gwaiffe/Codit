
from django.db import models

# create your models here


class Member(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class Saving(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.amount}"
