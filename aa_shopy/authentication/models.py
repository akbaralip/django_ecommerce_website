from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"
    
    