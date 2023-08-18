from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from store.models import *
from decimal import Decimal
from django.contrib.auth.models import User



# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=8, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    minimum_order_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    single_user_per_user = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.code
    
class Usercoupon(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    total_price = models.BigIntegerField()  




class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "No User"
        return f"Cart{self.pk} for {user_str}"

    
    def get_total_price(self):
        return self.cartitems_set.aggregate(total_price=Sum('price'))['total_price']


class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    



    def get_item_price(self):
        return Decimal(self.price)*Decimal(self.quantity)
    

    
class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"WishList for {self.user.username}"

class WishListItem(models.Model):
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE) 

    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    def get_item_price(self):

        return self.product.price   
    
