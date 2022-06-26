
import datetime
from itertools import product
from multiprocessing import context
from urllib import request
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth import login,logout,authenticate
from .models import *
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
import random
from twilio.rest import Client 
from django.http import JsonResponse
import json
from django.views.decorators.cache import never_cache
from decouple import config
import os
from django.db.models import Sum,Q,Min,Max
from twilio.rest import Client
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from .otp import *
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator



####################  login logout functions  ####################


@never_cache
def signup(request):
    users = CustomUser.objects.all()
    for user in users:
        if user.is_active == False:
            user.delete()
    try :
        device = request.COOKIES['device']
        customer = CustomUser.objects.get(device=device)
        signup_form = UserForm()
    except :
        signup_form = UserForm()
    if request.method == 'POST' :
        try :
            signup_form = UserForm(request.POST,instance=customer)
        except :
            signup_form = UserForm(request.POST)

        signup_number = request.POST.get('phone_number')
        signup_user = request.POST.get('username')
        email = request.POST.get('email')
        number = '+91' + str(signup_number)
    
        try:
            CustomUser.objects.get(email=email)
            messages.error(request,"Email already exists")
        except:
            try:
                CustomUser.objects.get(phone_number=signup_number)
                messages.error(request,"User Exists with this phone number")
            except:
                if signup_form.is_valid(): 
                    status = otp_login_code(request,number)
                    new_user = signup_form.save()
                    new_user.is_active = False
                    new_user.save()
                    request.session['signup_user'] = signup_user
                    return redirect('signup_otp_verify')
                             
    context = {'form' : signup_form}
    return render(request, 'signup.html', context)

   
def signup_otp_verify(request):
    refered_user = request.session.get('ref_user')
    signup_user = request.session.get('signup_user')
    new_user = CustomUser.objects.get(username = signup_user)
    signup_number = new_user.phone_number
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if len(str(otp)) < 4 or len(str(otp)) > 10 :
            messages.error(request,"Invalid Entry")
        else:
            username = signup_user
            number = '+91' + str(signup_number)
            status = otp_verify_code(request,number,otp)
            if status == 'approved':        
                if refered_user is not None:
                    try:
                        recommended_user = CustomUser.objects.get(id = refered_user)
                        new_user = CustomUser.objects.get(username=username)
                        Referal.objects.create(user = new_user,recommended_by = recommended_user)
                        ref_coupon = CouponDetail.objects.get(id = 1)  
                        UseCoupon.objects.create(user = new_user,coupon = ref_coupon)
                        UseCoupon.objects.create(user = recommended_user,coupon = ref_coupon)
                    except:
                        pass   
                CustomUser.objects.filter(username=username).update(device = None)
                CustomUser.objects.filter(username=username).update(is_active = True)
                login(request,new_user)
                return redirect('home')
            else:
                
                messages.error(request,"Incorrect OTP ")
                return render(request, 'signup_otp_verify.html')
    else :
        messages.success(request,"OTP has been sent to : "+ signup_number)
    return render(request, 'signup_otp_verify.html')


@never_cache
def resend_signup_otp(request):
    signup_user = request.session.get('signup_user')
    new_user = CustomUser.objects.get(username = signup_user)
    signup_number = new_user.phone_number
    number = '+91' + str(signup_number) 
    status = otp_login_code(request,number)
    return redirect('signup_otp_verify')


@never_cache    
def signin(request):
    if request.user.is_authenticated:
        return render(request,'index.html')
    if request.method == 'POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username= username , password = password)
        if user is not None :
            if user.blocked == False :
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,"You seems blocked try again later")
        else:
            messages.error(request,"Incorrect UserName Or Password")
    return render(request, 'signin.html')




def otp_login(request):
    if request.method == 'POST':
        phone = request.POST.get('mobile')
        request.session['phone'] = phone
        number = '+91' + str(phone)
        user = None
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except:
            
            messages.error(request,"There is no user with this phone number")
            return render(request, 'otp_login.html',)
        if user is not None:
            status = otp_login_code(request,number)
            return redirect('otpverify')
    return render(request, 'otp_login.html')




@never_cache
def resend_otp(request):
    phone = request.session.get('phone')
    number = '+91' + str(phone)
    user = None
    try:
        user = CustomUser.objects.get(phone_number=phone)
    except:        
        messages.error(request,"There is no user with this phone number")
        return render(request, 'otp_login.html',)
    if user is not None:
        status = otp_login_code(request,number)
        return redirect('otpverify')




@never_cache
def otpverify(request):
    phone = request.session.get('phone')
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if len(str(otp)) < 4 or len(str(otp)) > 10 :
            messages.error(request,"Invalid Entry")
        else:
            user = CustomUser.objects.get(phone_number= phone)
            username = user.username
            number = '+91' + str(phone)
            status = otp_verify_code(request,number,otp)
            if status == 'approved':
                if user.blocked == False :
                    login(request,user)
                    request.session['session_name'] = username
                    return redirect('home')
                else:
                    messages.error(request,"You seems blocked try again later")
            else:
                
                messages.error(request,"Incorrect OTP ")
                return render(request, 'otpverify.html')
    else :
        messages.success(request,"OTP has been sent to : "+ phone)
    return render(request, 'otpverify.html')

    




@never_cache
def signout(request):
    logout(request)
    return redirect("/")





####################  main functions  ####################


@never_cache
def home(request, *args, **kwargs):
    page = 'Home'
    code = str(kwargs.get('ref_code'))
    try:
        reference_user = CustomUser.objects.get(ref_code=code)
        request.session['ref_user'] = reference_user.id 
    except:
        pass 
    if request.user.is_authenticated:
        try :
            device = request.COOKIES['device']
            if device is not None :
                guest, created =CustomUser.objects.get_or_create(device=device, username=device)
                guest.delete()
        except:
            pass
        customer = request.user
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')
        wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
        cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device, username=device)
                order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')
                wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
                cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
        except:
            order = None
            wishes = None
            cart_num = None
    categories = Categorie.objects.all()   
    products = Product.objects.all()
    featured_products = Product.objects.all().exclude(product_category__c_offer = None , p_offer = None )
    p = Paginator(featured_products, 8)
    pg = request.GET.get('pg')
    featured_products = p.get_page(pg)
    banners = Banner.objects.all()
    context = {'cart_num': cart_num,'products':products , 'banners': banners, 'categories':categories, 'featured_products': featured_products,'page': page,'wishes':wishes}
    return render(request,'index.html',context)


@never_cache
def load_more_data(request):
    pass
#     offset = int(request.GET.get('offset'))
#     limit = int(request.GET.get('limit'))
#     products = Product.objects.all().order_by('-id')[offset:offset + limit]
#     t=render_to_string('ajax/product-list.html',{'products':products})
#     return JsonResponse({'data': t})


@never_cache
def main_shop(request):
    page = 'Shop'
    if request.user.is_authenticated:
        customer = request.user     
    else :        
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")

    categories = Categorie.objects.all()
    brands = Brand.objects.all()
    total_products = Product.objects.count()
    products = Product.objects.all().order_by('-id')
    min_price = Product.objects.aggregate(Min('product_price'))
    max_price = Product.objects.aggregate(Max('product_price'))
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')  
    context = {'products': products, 'cart_num': cart_num, 'categories':categories, 'brands':brands, 'total_products' : total_products,'page': page,'wishes':wishes,'min_price':min_price,'max_price':max_price}
    return render(request,'mainshop.html',context)


@never_cache
def filter_category(request,id):
    if request.user.is_authenticated:
        customer = request.user     
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")       
    brands = Brand.objects.all()
    cat_products = Product.objects.filter(product_category = id)
    cat = Categorie.objects.get(id = id)
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart') 
    context = {'products': cat_products , 'cart_num': cart_num, 'brands':brands,"cat":cat,'wishes':wishes}
    return render(request,'category.html',context)


@never_cache
def filter_category_products(request):
    if request.user.is_authenticated:
        customer = request.user     
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")       
    brands=request.GET.getlist('brand[]')
    categories = request.GET.getlist('category[]')
    id=request.GET['catId']
    cat_products = Product.objects.filter(product_category = id)
    if len(brands)>0:
        cat_products = cat_products.filter(brand__id__in=brands).distinct()
    
    if len(categories)>0:
        cat_products = cat_products.filter(product_category__id__in=categories).distinct()
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    t=render_to_string('ajax/product-list.html',{'products':cat_products,'wishes':wishes}) 
    return JsonResponse({'data': t})



@never_cache
def filter_shop_products(request):
    if request.user.is_authenticated:
        customer = request.user     
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")       
    brands=request.GET.getlist('brand[]')
    categories = request.GET.getlist('category[]')
    allProducts=Product.objects.all()
    if len(brands)>0:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()
    if len(categories)>0:
        allProducts = allProducts.filter(product_category__id__in=categories).distinct()
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    t=render_to_string('ajax/product-list.html',{'products':allProducts,'wishes':wishes})  
    return JsonResponse({'data': t})

@never_cache
def filter_by_price_range(request):
    page = 'Shop'
    if request.user.is_authenticated:
        customer = request.user     
    else :        
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin") 
    input_min = request.GET.get('input_min')
    input_max = request.GET.get('input_max')
    range_min = request.GET.get('range_min')
    range_max = request.GET.get('range_max')
    print(input_min, input_max, range_min, range_max)
    if range_min is not None and range_max is not None :
        products = Product.objects.filter(product_price__range=[range_min, range_max])
    elif input_min is not None and input_max is not None :
        products = Product.objects.filter(product_price__range=[input_min, input_max])
    else :
        products = Product.objects.all()
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    t=render_to_string('ajax/product-list.html',{'products':products,'wishes':wishes})  
    return JsonResponse({'data': t})


@never_cache
def sortproducts(request):
    if request.user.is_authenticated:
        customer = request.user     
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")       
    sortby = request.GET.get('sort')
    allProducts=Product.objects.all()
    if sortby == '1' :
        allProducts = allProducts.order_by('product_price')  
    elif sortby == '2' :
        allProducts = allProducts.order_by('-product_price')
    else :
        allProducts = allProducts.order_by('id')
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    t=render_to_string('ajax/product-list.html',{'products':allProducts,'wishes':wishes})  
    return JsonResponse({'data': t})
    


@never_cache
@login_required(login_url='signin')
def main_orders(request):
    page = 'Orders'
    customer = request.user
    orders = Orderdetail.objects.filter(order_customer = customer).exclude(order_status = 'Cart').exclude(order_status = 'Gobuy').order_by('-id')
    items = OrderItem.objects.all()
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart') 
    context = {'orders': orders, 'items' : items, 'cart_num' : cart_num,'page': page,}
    return render(request,'orders.html',context)


@never_cache
def wishlist(request):
    if request.user.is_authenticated:
        customer = request.user     
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")
    items = WishlistItem.objects.filter(user = customer)
    wishcount = WishlistItem.objects.filter(user = customer).count()
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart') 
    context = {'items': items, 'cart_num': cart_num,'wishcount': wishcount,}
    return render(request,'wishlist.html',context)

@never_cache
def wishlistitem(request, id):
    if request.user.is_authenticated:
        customer = request.user
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    product = Product.objects.get(pk = id)
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'product' : product, 'cart_num': cart_num,'wishes': wishes,}
    return render(request, 'wishlistsingle.html', context)

def remove_from_wishlist(request):
    id = request.GET.get('id')
    item = WishlistItem.objects.get(id = id)
    item.delete()
    return JsonResponse(data={'items':'item'})

@never_cache
def make_wish(request):
    if request.user.is_authenticated:
        customer = request.user
        
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    productId = request.GET.get('productId')
    print(productId)
    action = request.GET.get('action')
    print(action)
    product = Product.objects.get(id=productId)
    

    if action == 'add'  :
       wishes, created= WishlistItem.objects.get_or_create(user = customer, item_product=product)
    else :
        wishes = WishlistItem.objects.get(user = customer, item_product=product)
        wishes.delete()


    response = {'items':'flag'}
    return JsonResponse(response)



#################### product functions ####################


@never_cache
def category(request):
    pass



@never_cache
def singleproduct(request, id):
    if request.user.is_authenticated:
        customer = request.user
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    product = Product.objects.get(pk = id)
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'product' : product, 'cart_num': cart_num,'wishes': wishes,}
    return render(request, 'product.html', context)

@never_cache
def search(request):
    page = 'Shop'
    if request.user.is_authenticated:
        customer = request.user
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    keyword = request.GET['keyword']
    if keyword:
        products = Product.objects.filter(  Q(product_name__icontains=keyword) | Q(product_description__icontains=keyword) | Q(brand__brand_name__icontains=keyword) |Q(product_category__category_name__icontains=keyword) )
        productcount = products.count()
        if productcount == 0 :
            page = 'NoResult'
    else:
        page = 'NoResult'
    wishes = WishlistItem.objects.filter(user = customer).values_list('item_product', flat=True)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')  
    categories = Categorie.objects.all()
    brands = Brand.objects.all()
    context = {'products':products,'productcount':productcount,'cart_num':cart_num,'wishes': wishes,'categories':categories,'brands':brands,'page': page}
    return render (request,'mainshop.html',context)


####################  order functions  ####################


@never_cache
@login_required(login_url='signin')
def buynow(request,id):
    page = 'checkout_page'
    customer = request.user
    product = Product.objects.get(id=id)
    shipping = ShippingAddress.objects.filter(customer = customer)
    address_count = ShippingAddress.objects.filter(customer = customer).count()
    form = AddressForm()
    if request.method == 'POST' :
        form = AddressForm(request.POST)
        if form.is_valid() :
            var = form.save(commit=False)
            var.customer = customer
            var.save()
            return redirect('buynow',id = id)
    else :
        try :
            last = Orderdetail.objects.get(order_customer = customer,order_status = 'Gobuy')
            last.delete()
        except :
            pass
    
    order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
    if request.method == 'GET' :
        order.coupon_used = False
    items, created = OrderItem.objects.get_or_create(item_order=order, item_product=product,item_quantity = 1)
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'items': items, 'order': order, 'shipping': shipping,'form' : form , 'page': page,'cart_num': cart_num, 'address_count':address_count}
    return render(request,'checkout.html',context)


@never_cache
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    try :
        last = Orderdetail.objects.get(order_customer = customer,order_status = 'Gobuy')
        last.delete()
    except :
        pass
    order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')
    if request.method == 'GET' :
        order.coupon_used = False
    items = order.orderitem_set.all()
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'items': items, 'order': order, 'cart_num': cart_num}
    return render(request, 'cart.html',context)


@never_cache
def updateitem(request):
    if request.user.is_authenticated:
        customer = request.user
        
    else :
        try :
            device = request.COOKIES['device']
            if device is not None :
                customer, created = CustomUser.objects.get_or_create(device=device)
        except:
            return redirect("signin")   
    productId = request.GET.get('productId')
    print(productId)
    action = request.GET.get('action')
    print(action)
    product = Product.objects.get(id=productId)
    cur_stock = product.quantity_available
    order, created = Orderdetail.objects.get_or_create(order_customer = customer , order_status='Cart')
    orderItem, created = OrderItem.objects.get_or_create(item_order=order, item_product=product)

    
    if  cur_stock > orderItem.item_quantity :
        flag = 0
    else :
        flag = 1

    if action == 'add' and cur_stock > orderItem.item_quantity :
        orderItem.item_quantity = (orderItem.item_quantity + 1)
       
  
    elif action == 'remove' and orderItem.item_quantity > 1:

        orderItem.item_quantity = (orderItem.item_quantity - 1)
        if  cur_stock > orderItem.item_quantity :
            flag = 0
        else :
            flag = 1
    orderItem.save()
    if orderItem.item_quantity <= 0:
        orderItem.delete()
    response = {'items':order.get_cart_item,'quantity':orderItem.item_quantity,
    'total':orderItem.get_total,'cart_total':order.get_cart_total,'productId':productId,'cur_stock':cur_stock, 'flag':flag}
    return JsonResponse(response)


def remove_from_cart(request):
    id = request.GET.get('id')
    item = OrderItem.objects.get(id = id)
    item.delete()
    return JsonResponse(data={'items':'item'})


@never_cache
@login_required(login_url='signin')
def checkout(request):
    page = 'checkout_page'
    customer = request.user
    address_count = ShippingAddress.objects.filter(customer = customer).count()
    order = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    items = order.orderitem_set.all()
    shipping = ShippingAddress.objects.filter(customer = customer)
    form = AddressForm()
    if request.method == 'GET' :
        order.coupon_used = False
    if request.method == 'POST' :
        form = AddressForm(request.POST)
        if form.is_valid() :
            var = form.save(commit=False)
            var.customer = customer
            var.save()
            return redirect("checkout")     
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'items': items, 'order': order, 'shipping': shipping,'form' : form , 'page': page,'cart_num': cart_num,'address_count':address_count}
    return render(request,'checkout.html',context)


####################  coupon methods  ####################


@never_cache
@login_required(login_url='signin')
def coupon_verify(request):
    
    customer = request.user
    input_code = request.GET.get('input_code')
    try :
        
        apply_coupon = UseCoupon.objects.get(user = customer,checking = True,used =False )       
        apply_coupon.fororder = None
        apply_coupon.checking = False
        apply_coupon.save()
    except :
        pass
    try :
        coupon = CouponDetail.objects.get(code=input_code)
    except :
        data = {'total_amount' : None,'percentage':None,}
        return JsonResponse(data)
    last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
    if last.order_status == 'Gobuy' :
        order = Orderdetail.objects.get(order_customer = customer,order_status = 'Gobuy')
        items = OrderItem.objects.get(item_order = order)
    else :
        order= Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')  
        items = order.orderitem_set.all()
    lessed_money = (order.get_cart_total * coupon.offer_percentage / 100)
    old_price = order.get_cart_total
    try :
        apply_coupon = UseCoupon.objects.filter(user = customer,coupon = coupon,used = False).first()
        print(apply_coupon, order)
    except:
        data = {'total_amount' : None,'percentage':None,}
        return JsonResponse(data)
    if apply_coupon is None :
        data = {'total_amount' : None,'percentage':'used',}
        return JsonResponse(data)
    apply_coupon.fororder = order
    apply_coupon.checking = True
    apply_coupon.lessed_money = int(lessed_money)
    order.coupon_used = True
    order.save()
    apply_coupon.save()
    data = {'total_amount' : order.get_cart_total,'percentage':coupon.offer_percentage,'old_price':old_price }
    return JsonResponse(data)

@never_cache
@login_required(login_url='signin')
def removecoupon(request):
    pass


####################  payment methods  ####################


@never_cache
@login_required(login_url='signin')
def payment(request,id):
    page = 'payment_page'
    customer = request.user
    last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
    if last.order_status == 'Gobuy' :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
        items = OrderItem.objects.get(item_order = order)
    else :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')  
        items = order.orderitem_set.all()
    if request.method == 'GET' :
        order.coupon_used = False
       
        try :
           
            apply_coupon = UseCoupon.objects.get(user = customer,checking = True,used =False )
            
            apply_coupon.fororder = None
            
            apply_coupon.checking = False
            apply_coupon.save()
        except :
            pass
    shipping = ShippingAddress.objects.get( id = id)
    coupons= UseCoupon.objects.filter(user = customer).exclude(used = True)
    coupon_count = coupons.count()
    order.order_address = shipping
    order.save()
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'items': items, 'order': order, 'shipping': shipping, 'page' : page,'coupons':coupons,'coupon_count':coupon_count,'cart_num':cart_num}
    return render(request,'checkout.html',context)


@never_cache
@login_required(login_url='signin')
def proceed_cod(request):  
    customer = request.user
    last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
    if last.order_status == 'Gobuy' :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
        items = OrderItem.objects.get(item_order = order)
        current_stock = items.item_product.quantity_available
        new_stock = current_stock - 1
        Product.objects.filter(id = items.item_product.id ).update(quantity_available = new_stock)
    else :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')  
        items = order.orderitem_set.all()
        for item in items :
            ordered_items = item.item_quantity
            current_stock = item.item_product.quantity_available
            new_stock = current_stock - ordered_items
            product_id = item.item_product.id
            Product.objects.filter(id = product_id ).update(quantity_available = new_stock)
    total_amount = order.get_cart_total
    payobj, created = Payment.objects.get_or_create(payment_method = 'Cash On Delevery',total_amount = total_amount, order = order,payment_status = 'None' )
    order.order_date = datetime.date.today()
    order.order_status = 'Placed'
    try :
        apply_coupon = UseCoupon.objects.get(fororder=order,used = False,checking = True)
        coupon_id = apply_coupon.coupon.id
        coupon = CouponDetail.objects.get(id = coupon_id )
        apply_coupon.used = True
        coupon.use_count = coupon.use_count + 1
        coupon.total_lessed_money = coupon.total_lessed_money + apply_coupon.lessed_money
        apply_coupon.save()
        coupon.save()

    except :
        pass
    if payobj.payment_status == 'None' :
        payobj.payment_status = 'Incomplete'
    payobj.save()
    order.save()
    return JsonResponse(data={'items':'item'})


@never_cache
@login_required(login_url='signin')
def pay_razorpay(request):
    customer = request.user  
    last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
    if last.order_status == 'Gobuy' :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
    else :
        order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')  
    total_price =  order.get_cart_total
    email = customer.email
    full_name = customer.first_name + ' ' + customer.last_name
    phone_number = customer.phone_number
    return JsonResponse({"total_price":total_price, "email":email,"full_name":full_name,"phone_number":phone_number, })

@ csrf_exempt
@login_required(login_url='signin')
def order_by_razorpay(request):
    if request.method == 'POST':       
        customer = request.user
        last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
        if last.order_status == 'Gobuy' :
            order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
            items = OrderItem.objects.get(item_order = order)
            current_stock = items.item_product.quantity_available
            new_stock = current_stock - 1
            Product.objects.filter(id = items.item_product.id).update(quantity_available = new_stock)
        else :
            order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')  
            items = order.orderitem_set.all()
            for item in items :
                ordered_items = item.item_quantity
                current_stock = item.item_product.quantity_available
                new_stock = current_stock - ordered_items
                product_id = item.item_product.id
                Product.objects.filter(id = product_id).update(quantity_available = new_stock)
        total_amount = order.get_cart_total
        transaction_id = request.POST.get('order_id')
        Payment.objects.get_or_create(order = order,payment_method = 'Razor Pay',total_amount = total_amount,payment_status = 'Completed', transaction_id = transaction_id)
        order.order_date = datetime.date.today()
        order.order_status = 'Placed'
        try :
            apply_coupon = UseCoupon.objects.get(fororder=order,used = False,checking = True)
            coupon_id = apply_coupon.coupon.id
            coupon = CouponDetail.objects.get(id = coupon_id )
            apply_coupon.used = True
            coupon.use_count = coupon.use_count + 1
            coupon.total_lessed_money = coupon.total_lessed_money + apply_coupon.lessed_money
            apply_coupon.save()
            coupon.save()
        except :
            pass
        order.save()
        return JsonResponse({'status': 'Your order has been Placed Successfully'})



@ csrf_exempt
@login_required(login_url='signin')
def order_by_paypal(request):
    if request.method == 'POST':        
        customer = request.user
        last = Orderdetail.objects.filter(order_customer = customer).order_by('-id')[0]
        if last.order_status == 'Gobuy' :
            order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Gobuy')
            items = OrderItem.objects.get(item_order = order)
            current_stock = items.item_product.quantity_available
            new_stock = current_stock - 1
            Product.objects.filter(id = items.item_product.id).update(quantity_available = new_stock)
        else :
            order, created = Orderdetail.objects.get_or_create(order_customer = customer,order_status = 'Cart')  
            items = order.orderitem_set.all()
            for item in items :
                ordered_items = item.item_quantity
                current_stock = item.item_product.quantity_available
                new_stock = current_stock - ordered_items
                product_id = item.item_product.id
                Product.objects.filter(id = product_id).update(quantity_available = new_stock)
        total_amount = order.get_cart_total
        transaction_id = request.POST.get('order_id')
        Payment.objects.get_or_create(order = order,payment_method = 'Paypal',total_amount = total_amount,payment_status = 'Completed', transaction_id = transaction_id)
        order.order_date = datetime.date.today()
        order.order_status = 'Placed'
        try :
            apply_coupon = UseCoupon.objects.get(fororder=order,used = False,checking = True)
            coupon_id = apply_coupon.coupon.id
            coupon = CouponDetail.objects.get(id = coupon_id )
            apply_coupon.used = True
            coupon.use_count = coupon.use_count + 1
            coupon.total_lessed_money = coupon.total_lessed_money + apply_coupon.lessed_money
            apply_coupon.save()
            coupon.save()
        except :
            pass
        order.save()
        return JsonResponse({'status': 'Your order has been Placed Successfully'})


####################  profile functions  ####################


@never_cache
@login_required(login_url='signin')
def account(request):
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'user': customer, 'cart_num': cart_num}
    return render(request, 'user/personaldetailes.html',context)


@never_cache
@login_required(login_url='signin')
def invoice(request,id):
    user = request.user
    order = Orderdetail.objects.get(id=id)
    items = order.orderitem_set.all()
    order, created = Orderdetail.objects.get_or_create(order_customer = user,order_status = 'Cart')
    cart_num = Orderdetail.objects.get(order_customer = user,order_status = 'Cart')
    context = {'items': items, 'order': order, 'user': user,'cart_num': cart_num}

    return render(request, 'user/invoice.html',context)


@never_cache
@login_required(login_url='signin')
def profile_order(request):   
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    orders = Orderdetail.objects.filter(order_customer = customer).exclude(order_status = 'Cart').exclude(order_status = 'Gobuy').order_by('-id')
    items = OrderItem.objects.all()
    context = {'orders': orders, 'items' : items, 'cart_num' : cart_num}
    return render(request, 'user/orderdetailes.html',context)


@never_cache
@login_required(login_url='signin')
def cancelorder(request, id):
    order = Orderdetail.objects.get(id = id)
    items = OrderItem.objects.filter(item_order = order)
    for item in items :
            ordered_items = item.item_quantity
            current_stock = item.item_product.quantity_available
            new_stock = current_stock + ordered_items
            product_id = item.item_product.id
            Product.objects.filter(id = product_id).update(quantity_available = new_stock)
    order.order_status = 'Cancellation Requested'
    order.save()
    return redirect("profile_order")    


@never_cache
@login_required(login_url='signin')
def returnorder(request, id):
     order = Orderdetail.objects.get(id = id)
     order.order_status = 'Return'
     order.save()
     return redirect("profile_order")


@never_cache
@login_required(login_url='signin')
def profile_password(request):
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    context = {'cart_num': cart_num}
    return render(request, 'user/changepassword.html', context)


@never_cache
@login_required(login_url='signin')
def user_coupons(request):  
    user = request.user
    cart_num = Orderdetail.objects.get(order_customer = user,order_status = 'Cart')
    coupons= UseCoupon.objects.filter(user = user).exclude(used = True)
    context ={'coupons': coupons, 'cart_num': cart_num}
    return render(request, 'user/coupondetailes.html',context)


@never_cache
@login_required(login_url='signin')
def profile_shipping(request):  
    user = request.user
    cart_num = Orderdetail.objects.get(order_customer = user,order_status = 'Cart')
    shipping= ShippingAddress.objects.filter( customer = user)
    context ={'shipping': shipping, 'cart_num': cart_num}
    return render(request, 'user/shippingaddress.html',context)


@never_cache
@login_required(login_url='signin')
def delete_ship_address(request):
    id = request.GET.get('id')
    user = request.user
    ShippingAddress.objects.get(id=id).delete()
    return JsonResponse(data={'items':'item'})


@never_cache
@login_required(login_url='signin')
def addnewad(request):
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    form = AddressForm()   
    if request.method == 'POST' :
        form = AddressForm(request.POST)
        if form.is_valid() :
            var = form.save(commit=False)
            var.customer = customer
            var.save()
            return redirect("profile_shipping")   
    context ={'form' : form, 'cart_num': cart_num}
    return render(request, 'user/addnewad.html',context)


@never_cache
@login_required(login_url='signin')
def edit_shipping_ad(request,id):
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    address = ShippingAddress.objects.get(id=id)
    form =  AddressForm(instance=address)
    context ={'form' : form, 'cart_num': cart_num}
    if request.method == 'POST' :
        form = AddressForm(request.POST, instance=address)
        if form.is_valid() :
            form.save()
            return redirect("account")
    return render(request, 'user/addnewad.html',context)


@never_cache
@login_required(login_url='signin')
def edit_address(request):
    #this is for user details updation 
    customer = request.user
    cart_num = Orderdetail.objects.get(order_customer = customer,order_status = 'Cart')
    form =  UserUpdateForm(instance=request.user)
    context ={'form' : form, 'cart_num': cart_num}
    if request.method == 'POST' :
        form = UserUpdateForm(request.POST, instance=request.user)
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        if username != request.user.username or email != request.user.email or phone_number != request.user.phone_number :
            try:
                CustomUser.objects.get(username=username)
                messages.error(request,"Username already exists")
            except:
                try:
                    CustomUser.objects.get(email=email)
                    messages.error(request,"Email already exists")
                except:
                    try:
                        CustomUser.objects.get(phone_number=phone_number)
                        messages.error(request,"User Exists with this phone number")
                    except:
                        pass
        if form.is_valid() :
            form.save()
            return redirect("account")
    return render(request, 'user/edit_address.html',context)
    
class MyPasswordChangeView(PasswordChangeView):

    template_name = 'user/changepassword.html'
    success_url = reverse_lazy('password-change-done-view')
   

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/passwordchanged.html'
    


   
