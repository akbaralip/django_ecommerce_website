from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True, null=True)
    postal_code = models.CharField(50)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=500)
    is_delivery_address = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.first_name}, {self.email}, {self.state}"
    

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet: {self.balance}"
    
    @receiver(post_save, sender=User)
    def create_wallet(sender, instance, created, **kwargs):
        if created:
            Wallet.objects.create(user=instance)


    
class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    order_id = models.ForeignKey('orders.Order', on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=(
        ('PURCHASE','purchase'),
        ('CANCEL','cancel'),
        ('RETURN','return'),
    ))
    
    def __str__(self):
        return f"Wallet Transaction:{self.amount} - {self.date}"
    
    
    


