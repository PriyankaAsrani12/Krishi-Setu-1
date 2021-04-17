from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    is_farmer=models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    first_name=models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    phoneNumber = models.CharField(max_length=10)
    cardNumber = models.CharField(max_length=12)
    email = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    email = models.CharField(max_length=50)
    fssai=models.CharField(max_length=50)

    def __str__(self):
        return self.user.username