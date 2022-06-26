#home
from dataclasses import fields
from email.headerregistry import Address
from pyexpat import model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms


class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username','email','phone_number','password1','password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username','email','phone_number']

class ResetPassword(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['password']

class AddressForm(forms.ModelForm):
    
    class Meta :
        model = ShippingAddress
        fields = ['address_name', 'full_name', 'phone_number','pincode','place','locality_address','city_district','state']
        labels = {
            'address_name' : 'Address',
            'full_name' : 'Full Name',
            'phone_number' : 'Phone Number',
            'pincode' : 'Pincode',
            'place' : 'Place',
            'locality_address' : 'House/Flat Number and Name,Area and Street ',
            'city_district' : 'City/District',
            'state' : 'State',
        }

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)

payment_choices= [

    ('Cash on delivery','Cash on delivery'),
    ('Paypal', 'Paypal'),
    ('razorpay','razorpay')
]

class PaymentModeRadioForm(forms.Form):

    payvia= forms.CharField(
        widget=forms.RadioSelect(choices=payment_choices))


