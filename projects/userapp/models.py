
import email
from itertools import product
from statistics import mode
from unicodedata import category, name
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from .utils import generate_ref_code
# Create your models here.

class Brand(models.Model):
    brand_name = models.CharField(max_length=70)

    def __str__(self):
        return str(self.brand_name)

class ProductOffer(models.Model):
    name = models.CharField(max_length=50, null=True)
    percent = models.FloatField(validators=[MinValueValidator(1),MaxValueValidator(90)],max_length=30,default=1,null=True)
    description = models.CharField(max_length=200, null=True, blank=True)

class CategoryOffer(models.Model):
    name = models.CharField(max_length=50, null=True)
    percent = models.FloatField(validators=[MinValueValidator(1),MaxValueValidator(90)],max_length=30,default=1,null=True)
    description = models.CharField(max_length=200, null=True, blank=True)




class Categorie(models.Model):
    category_name = models.CharField(max_length=50)
    category_img = models.ImageField(upload_to = 'product_images', null=True, )
    footer = models.CharField(max_length=200, null=True, blank=True)
    c_offer = models.ForeignKey(CategoryOffer,models.SET_NULL,max_length=30,blank=True,null=True)

    def __str__(self):
        return str(self.category_name)



class Product(models.Model):
    Gender_Choices = (
        ('M','Male'),
        ('F','Female'),
        ('N','Not Specified'),
    )
    product_name = models.IntegerField(unique=True)
    product_image = models.ImageField(upload_to = 'product_images')
    product_img_left = models.ImageField(upload_to = 'product_images')
    product_img_right = models.ImageField(upload_to = 'product_images')
    product_category = models.ForeignKey(Categorie,on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True,blank=True)
    product_description = models.CharField(max_length=200)
    product_price = models.PositiveIntegerField(null=True,default=0)
    quantity_available = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=1, choices=Gender_Choices, default='N', null=True, blank=True)
    new = models.BooleanField(default=False, null=True, blank=True)
    p_offer = models.ForeignKey(ProductOffer,models.SET_NULL,max_length=30,blank=True,null=True)

    @property
    def product_discount_price(self):
        try :
            pro_ = self.p_offer.percent
            cat_ = self.product_category.c_offer.percent
            if cat_ < pro_ :
                price = self.product_price - (self.product_price * pro_ / 100)
            else :
                price = self.product_price - (self.product_price * cat_ / 100)
        except :
            try : 
                pro_ = self.p_offer.percent
                price = self.product_price - (self.product_price * pro_ / 100) 
            except :
                try :
                    cat_ = self.product_category.c_offer.percent
                    price = self.product_price - (self.product_price * cat_ / 100)
                except :
                    price = self.product_price
        return round(price,2)

       

    def __str__(self):
        return str(self.product_name)




class CustomUser(AbstractUser):
    blocked = models.BooleanField(default=False,)
    phone_regex = RegexValidator(regex=r'^1?\d{9,15}$', message="Invalid Phone Number")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, null=True) # validators should be a list
    device = models.CharField(max_length=200, null=True, blank=True)
    order_count = models.IntegerField(default=0, null=True)
    ref_code = models.CharField(max_length=12,blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.ref_code == None:
            code = generate_ref_code()
            self.ref_code = code
        super().save(*args,**kwargs)


class Referal(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    recommended_by = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, blank=True, null=True,related_name='ref_by')

class ShippingAddress(models.Model):
    address_type = (
        ('Home','Home'),
        ('Work','Work'), 
    )
    address_name = models.CharField(max_length=20,choices=address_type, default= 'Home')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE , blank=True, null=True)  
    full_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    pincode = models.CharField(max_length=10)
    place = models.CharField(max_length=100,null= True ,blank=True)
    locality_address= models.CharField(max_length=100)
    city_district = models.CharField(max_length=100)
    state = models.CharField(max_length=30)

def __str__(self):
        return str(self.address_name)



class Orderdetail(models.Model):
    order_status_list = (
        ('Cart','Cart'),
        ('Gobuy','Gobuy'),
        ('Placed','Placed'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Cancellation Requested', 'Cancellation Requested'),
        ('Failed','Failed'),
        ('Shipped', 'Shipped' ),
        ('Out Of Delevery', 'Out Of Delevery'),
        ('Return','Return'),
    )
    order_date = models.DateField(null= True ,blank=True)
    order_status = models.CharField(max_length=30, choices=order_status_list, default='Processing', )
    order_customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL , blank=True, null=True)
    order_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL , blank=True, null=True)
    order_id = models.CharField(max_length= 100,null= True ,blank=True)
    coupon_used = models.BooleanField(default=False)
    @property
    def get_cart_total(self):
        
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        if self.coupon_used == False:
            return total
        else :
            try :
                total = total - self.usecoupon.lessed_money
            except:
                pass
            return total

    
    @property
    def get_cart_item(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.item_quantity for item in orderitems])
        return total
    
    def __str__(self):
        return str(self.id)

class OrderItem(models.Model):
    
    item_order = models.ForeignKey(Orderdetail, on_delete=models.CASCADE, blank=True, null=True)
    item_product = models.ForeignKey(Product, on_delete=models.SET_NULL , blank=True, null=True)
    item_quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    

    @property
    def get_total(self):
        total = str(int(self.item_product.product_discount_price) * int(self.item_quantity))
        return int(total)

    def __str__(self):
        return str(self.item_product)

class WishlistItem(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item_product = models.ForeignKey(Product, on_delete=models.SET_NULL , blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.item_product)


class Payment(models.Model):
    
    status_list = (
        ('None','None'),
        ('Incomplete', 'Incomplete'),
        ('Processing','Processing'),
        ('Completed','Completed'),
        ('Failed','Failed'),
    )
    total_amount = models.FloatField(max_length=30,default=0)
    payment_method = models.CharField(max_length=30, )
    payment_status = models.CharField(max_length=30, choices=status_list, default='None', )
    order =  models.OneToOneField(Orderdetail, on_delete=models.CASCADE)  
    transaction_id = models.CharField(max_length= 100,null= True ,blank=True)



class CouponDetail(models.Model):
    name = models.CharField(max_length=30,null= True, blank=True)
    code = models.CharField(max_length=30)
    offer_percentage = models.FloatField(validators=[MinValueValidator(1),MaxValueValidator(90)],max_length=30,default=1)
    created_date = models.DateField(auto_now_add=True)
    exp_date = models.DateField(null=True, blank=True)
    use_count= models.FloatField(max_length=30,default=0)
    total_lessed_money = models.FloatField(max_length=30,default=0)
    active = models.BooleanField(default=True,null=True)

class UseCoupon(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    fororder = models.OneToOneField(Orderdetail, on_delete=models.SET_NULL,blank=True, null=True)
    coupon = models.ForeignKey(CouponDetail, on_delete=models.CASCADE, blank=True, null=True)
    used = models.BooleanField(default=False,)
    lessed_money = models.FloatField(max_length=30,default=0)
    checking = models.BooleanField(default=False)

class Banner(models.Model):
    related_coupon = models.OneToOneField(CouponDetail, on_delete=models.CASCADE, blank=True, null=True)
    banner_image = models.ImageField(upload_to = 'product_images')
    name = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
   

    def __str__(self):
        return str(self.header)


   
