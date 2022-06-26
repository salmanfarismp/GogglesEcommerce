from cProfile import label
from dataclasses import field
from django import forms
from userapp.models import *



class Categorieoffers_form(forms.ModelForm):
    
    class Meta :
        model = CategoryOffer
        fields = ('name','percent','description')
        labels = {
            'name' : 'Name',
            'percent' : 'Percent',
            'description' : 'Description',
            
            
        }
    def __init__(self, *args, **kwargs):
        super(Categorieoffers_form, self).__init__(*args, **kwargs)
        self.fields['percent'].widget.attrs.update(
            {'min': 1, 'max':90})
    
class Productoffers_form(forms.ModelForm):
    
    class Meta :
        model = ProductOffer
        fields = ('name','percent','description')
        labels = {
            'name' : 'Name',
            'percent' : 'Percent',
            'description' : 'Description',
            
            
        }
    def __init__(self, *args, **kwargs):
        super(Productoffers_form, self).__init__(*args, **kwargs)
        self.fields['percent'].widget.attrs.update(
            {'min': 1, 'max':90})


class Categories_form(forms.ModelForm):
    
    class Meta :
        model = Categorie
        fields = ('category_name','category_img',)
        labels = {
            'category_name' : 'Category Name',
            'category_img' : 'Banner Image',
            
            
        }
    def __init__(self, *args, **kwargs):
        super(Categories_form, self).__init__(*args, **kwargs)

class Brand_form(forms.ModelForm):
    
    class Meta :
        model = Brand
        fields = ('brand_name',)
        labels = {
            'brand_name' : 'Brand Name',
            
            
            
        }
    def __init__(self, *args, **kwargs):
        super(Brand_form, self).__init__(*args, **kwargs)

class Coupon_form(forms.ModelForm):

    class Meta :
        model = CouponDetail
        fields = ('name','code','offer_percentage',)
        labels = {
            'name' : 'Coupon Name',
            'code' : 'Coupon Code',
            'offer_percentage' : 'Reduction Percentaage',
             
        }
             
     
    def __init__(self, *args, **kwargs):
        super(Coupon_form, self).__init__(*args, **kwargs)
        self.fields['offer_percentage'].widget.attrs.update(
            {'min': 1, 'max':90})
        


class products_form(forms.ModelForm):
    
    class Meta :
        model = Product
        fields = ('product_name','product_image','product_img_left',
        'product_img_right', 'product_category','brand', 'product_description',
         'product_price','quantity_available', 'gender', 'new',)
        labels = {
            'product_name' : 'Product Name',
            'product_image' : 'Main Image',
            'product_img_left' : 'Image 2',
            'product_img_right' : 'Image 3',
            'product_category' : 'Category',
            'brand' : 'Brand',
            'product_description': 'Product Description',
            'product_price' : 'Price',
            'quantity_available' : 'Available Quantity',
            'gender' : 'Gender',
            'new' : 'New',
            
        }


    def __init__(self, *args, **kwargs):
        super(products_form, self).__init__(*args, **kwargs)


class banner_form(forms.ModelForm):
    
    class Meta :
        model = Banner
        fields = ('name','banner_image','header',
        'description',)
        labels = {
            'name' : 'Banner Name',
            'banner_image' : 'Banner Image',
            'header' : 'Main Header',
            'description' : 'Description',
           
        }


    def __init__(self, *args, **kwargs):
        super(banner_form, self).__init__(*args, **kwargs)



update_choices= [

    ('Placed','Placed'),
    ('Shipped', 'Shipped'),
    ('Out Of Delivery','Out Of Delivery'),
    ('Completed','Completed'),
    ('Failed','Failed'),

]

class OrderUpdation(forms.Form):

    order_status = forms.CharField(
        label='Select The Order Status', widget=forms.Select(choices=update_choices))

    