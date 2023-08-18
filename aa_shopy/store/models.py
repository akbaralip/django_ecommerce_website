
# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

class BannerImage(models.Model):
    name=models.CharField(max_length=100)
    image = models.ImageField(upload_to='banner_images/')

    def __str__(self):
        return self.name
    

class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    


class Category(models.Model):
    name=models.CharField( max_length=100)
    image=models.ImageField(upload_to='category_images')
    is_active=models.BooleanField(default=True)
    
   
    slug=models.SlugField(max_length=250,unique=True,blank=True)

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)

class Brands(models.Model):
    name=models.CharField( max_length=100)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    slug=models.SlugField(blank=True)
    is_active=models.BooleanField(default=True)
    brand_name=models.ForeignKey(Brands,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args, **kwargs)

    

class Color(models.Model):
    color=models.CharField(max_length=10)

    def __str__(self):
        return self.color
    
class ProductVariant(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    color=models.ForeignKey(Color,on_delete=models.CASCADE)
    store_price=models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    sale_price =models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    discount_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    model_name =models.CharField(max_length=100)
    stock=models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    slug=models.SlugField(blank=True,unique=True)

    def __str__(self):
        return f"{self.product.name}-{self.color}"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            slug_str=f"{self.product.name}-{self.color}"
            self.slug=slugify(slug_str)
        super().save(*args, **kwargs)
    
    
class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.variant}-{self.image}"