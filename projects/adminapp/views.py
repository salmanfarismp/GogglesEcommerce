from calendar import c
from multiprocessing import context
from unicodedata import category
from unittest import result
from django.shortcuts import render
from django.shortcuts import render,redirect
from userapp.models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login,logout,authenticate
from .forms import *
from django.http import JsonResponse,HttpResponse
from django.views.decorators.cache import never_cache
import datetime
from django.views.generic import TemplateView
from datetime import date
from datetime import timedelta
from django.db.models import Sum,Q,Max
import csv
import xlwt
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import tempfile
from django.core.paginator import Paginator


@never_cache
@login_required(login_url='/iamadmin/')
def admin_home(request):
    page = 'dashboard'
    products = Product.objects.all()
    prod = []
    st = []
    for product in products:
        prod.append(product.product_name)
        st.append(product.quantity_available)
    max_product_stock = Product.objects.aggregate(Max('quantity_available'))
    placed = Orderdetail.objects.filter(order_status= 'Placed').count()
    shipped = Orderdetail.objects.filter(order_status= 'Shipped').count()
    completed = Orderdetail.objects.filter(order_status= 'Completed').count()
    cancelled = Orderdetail.objects.filter(order_status= 'Cancelled').count()
    out_of_delivery = Orderdetail.objects.filter(order_status= 'Out Of Delevery').count()
    returned = Orderdetail.objects.filter(order_status= 'Return').count()
    order_status = [placed,shipped,out_of_delivery,completed,cancelled,returned]
    cod = Payment.objects.filter(payment_method = 'Cash On Delevery').count()
    paypal = Payment.objects.filter(payment_method = 'Paypal').count()
    razorpay = Payment.objects.filter(payment_method = 'Razor Pay').count()
    payment_type = [cod,paypal,razorpay] 
    orderitems = OrderItem.objects.filter(item_order= completed)
    customers = CustomUser.objects.all().exclude(phone_number= None).count()
    orders = Orderdetail.objects.all().exclude(order_status = 'Cart').exclude(order_status = 'Gobuy').count()
    product_count = Product.objects.all().count()
    total_revenue = Payment.objects.all().aggregate(Sum('total_amount'))
    context = {'products':products,'order_status': order_status, 'payment_type': payment_type, 
     'customers':customers,'orders': orders,'prod': prod,'st':st, 'product_count':product_count,'total_revenue':total_revenue,'page': page,'max_product_stock':max_product_stock}
    return render(request,'admin_home.html',context)


@never_cache
def admin_search(request):
    keyword = request.GET['keyword']
    page = request.GET.get('page')
    if keyword:
        if page == 'dashboard' :
            return redirect('admin_home')
        elif page == 'salesreport':
            request.session['keyword'] = None
            request.session['filter_month'] = None
            request.session['filter_year'] = None
            request.session['filter_from_date'] = None
            request.session['filter_to_date'] = None
            request.session['keyword'] = keyword
            order_data = Orderdetail.objects.filter(payment__payment_status='Completed').filter( Q(order_date__icontains=keyword) | Q(order_id__icontains=keyword) | Q(order_customer__username__icontains=keyword) | Q(payment__payment_method__icontains=keyword)   )
            yr = []
            ag = 2000
            for i in range(0,51):
                yr.append(ag + i)
            context = {'order_data': order_data, 'years': yr,'page': page,}
            return render(request,'sales_report.html', context)
        elif page == 'userpage' :
            userlist = CustomUser.objects.filter( Q(username__icontains=keyword) | Q(id__icontains=keyword)  )
            context = {'user_list': userlist,'page': page,}
            return render(request,'users_table.html',context)
        elif page == 'categorypage' :
            categories = Categorie.objects.filter( Q(category_name__icontains=keyword) | Q(id__icontains=keyword)  )
            context = {'categories': categories,'page': page}
            return render(request,'categories_table.html',context)
        elif page == 'brandpage' :
            brands = Brand.objects.filter( Q(brand_name__icontains=keyword) | Q(id__icontains=keyword)  )
            context = {'brands': brands,'page': page}
            return render(request,'brands.html',context)
        elif page == 'productpage' :
            products = Product.objects.filter( Q(product_name__icontains=keyword) | Q(id__icontains=keyword) | Q(brand__brand_name__icontains=keyword) | Q(product_category__category_name__icontains=keyword) )
            context = {'products': products,'page': page}
            return render(request,'products_table.html',context)
        elif page == 'orderpage' :
            orderdetails = Orderdetail.objects.all().exclude(order_status='Cart').exclude(order_status='Gobuy').filter( Q(order_status__icontains=keyword) | Q(id__icontains=keyword) | Q(order_customer__username__icontains=keyword) | Q(payment__payment_method__icontains=keyword)  ).order_by('-payment')
            context = {'orderdetails' : orderdetails,'page': page,}
            return render(request,'order_table.html',context)
        elif page == 'bannerpage' :
            banners = Banner.objects.filter( Q(name__icontains=keyword) | Q(header__icontains=keyword) | Q(description__icontains=keyword)  )
            context = {'banners' : banners,'page': page,}
            return render(request,'banner_table.html',context)
        elif page == 'couponcreatepage' :
            coupons = CouponDetail.objects.filter( Q(name__icontains=keyword) | Q(code__icontains=keyword) | Q(offer_percentage__icontains=keyword)  )
            today = date.today()
            print(today)
            context = {'coupons' : coupons ,'date' : today,'page':page}
            return render(request,'coupon_table.html',context)
        elif page == 'couponusepage' :
            coupons = UseCoupon.objects.exclude(used = False).filter( Q(user__username__icontains=keyword) | Q(coupon__name__icontains=keyword)  )
            context = {'coupons' : coupons ,'page': page,}
            return render(request,'coupon_usage.html',context)
        elif page == 'categoryofferpage' :
            offers = CategoryOffer.objects.filter( Q(name__icontains=keyword) | Q(percent__icontains=keyword) | Q(id__icontains=keyword)  )
            context = {'offers': offers,'page': page}
            return render(request,'categoryoffers.html',context)
        elif page == 'productofferpage' :
            offers = ProductOffer.objects.filter( Q(name__icontains=keyword) | Q(percent__icontains=keyword) | Q(id__icontains=keyword)  )
            context = {'offers': offers,'page': page}
            return render(request,'productoffers.html',context)


        products = Product.objects.filter(  Q(product_name__icontains=keyword) | Q(product_description__icontains=keyword) | Q(brand__brand_name__icontains=keyword) |Q(product_category__category_name__icontains=keyword) )
        productcount = products.count()
        if productcount == 0 :
            page = 'NoResult'

    categories = Categorie.objects.all()
    brands = Brand.objects.all()
    context = {'products':products,'productcount':productcount,'categories':categories,'brands':brands,'page': page}
    return render (request,'mainshop.html',context)

@never_cache
@login_required(login_url='/iamadmin/')
def sales_report(request):


    note = 'Nothing'
    request.session['keyword'] = None
    request.session['filter_month'] = None
    request.session['filter_year'] = None
    request.session['filter_from_date'] = None
    request.session['filter_to_date'] = None
    page = 'salesreport'
    order_data = Orderdetail.objects.filter(payment__payment_status='Completed')
    yr = []
    ag = 2000
    months = ['January', 'February', 'March','April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for i in range(0,23):
        yr.append(ag + i)
    try:
        datestr = request.GET.get('dates')
            #start date
        mo = datestr[:2]
        da = datestr[3:5]
        ye = datestr[6:10]
        #enddate
        mo1 = datestr[13:15]
        da1 = datestr[16:18]
        ye1 = datestr[19:]
        from_date = ye+'-'+mo+'-'+da
        to_date = ye1+'-'+mo1+'-'+da1
        year = request.GET.get('year')
        month = request.GET.get('month')
        print(month)
        m = month
        print(m)
        print(from_date)
        if  month != '' :
            request.session['filter_month'] = m
            order_data = Orderdetail.objects.filter(order_date__month=m).filter(payment__payment_status='Completed').order_by('order_date')
        elif  year != '' :
            request.session['filter_year'] = year
            order_data = Orderdetail.objects.filter(order_date__year=year).filter(payment__payment_status='Completed').order_by('order_date')
        elif from_date != '' and to_date != '' :
            request.session['filter_from_date'] = from_date
            request.session['filter_to_date'] = to_date
            order_data = Orderdetail.objects.filter(order_date__range=[from_date,to_date]).filter(payment__payment_status='Completed').order_by('order_date')

    except:
        pass

    order_count = order_data.count()
    if order_count == 0 :
            note = 'NoResult'
    context = {'order_data': order_data, 'years': yr,'page': page,'months':months,'note': note}
    return render(request,'sales_report.html', context)



@never_cache
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)   
    writer.writerow(['User Id','Name','Number Of Products','Order Date','Amount','Payment Type'])
    
    keyword = request.session['keyword']
    if keyword is not None :
        order_data = Orderdetail.objects.filter(payment__payment_status='Completed').filter( Q(order_date__icontains=keyword) | Q(order_id__icontains=keyword) | Q(order_customer__username__icontains=keyword) | Q(payment__payment_method__icontains=keyword)   )
    else :
        order_data = Orderdetail.objects.filter(payment__payment_status='Completed')
    try :
        m = request.session['filter_month']
        year = request.session['filter_year']
        from_date = request.session['filter_from_date']
        to_date = request.session['filter_to_date']
        if  m is not None:
            order_data = Orderdetail.objects.filter(order_date__month=m).filter(payment__payment_status='Completed').order_by('order_date')
        elif  year is not None:
            order_data = Orderdetail.objects.filter(order_date__year=year).filter(payment__payment_status='Completed').order_by('order_date')
        elif from_date is not None and to_date is not None:
            order_data = Orderdetail.objects.filter(order_date__range=[from_date,to_date]).filter(payment__payment_status='Completed').order_by('order_date')
    except:
        pass
    
    for data in order_data:
        writer.writerow([data.id, data.order_customer, data.get_cart_item, data.order_date,data.payment.total_amount , data.payment.payment_method])
    
    return response

@never_cache
def export_excel(request):

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales Report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['User Id','Name','Order Date','Amount','Payment Type']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style = xlwt.XFStyle()
    keyword = request.session['keyword']
    if keyword is not None :
        order_data = Orderdetail.objects.filter(payment__payment_status='Completed').filter( Q(order_date__icontains=keyword) | Q(order_id__icontains=keyword) | Q(order_customer__username__icontains=keyword) | Q(payment__payment_method__icontains=keyword)   )
    else :
        order_data = Orderdetail.objects.filter(payment__payment_status='Completed')
    try :
        m = request.session['filter_month']
        year = request.session['filter_year']
        from_date = request.session['filter_from_date']
        to_date = request.session['filter_to_date']
        if  m is not None:
            order_data = Orderdetail.objects.filter(order_date__month=m).filter(payment__payment_status='Completed').order_by('order_date')
        elif  year is not None:
            order_data = Orderdetail.objects.filter(order_date__year=year).filter(payment__payment_status='Completed').order_by('order_date')
        elif from_date is not None and to_date is not None:
            order_data = Orderdetail.objects.filter(order_date__range=[from_date,to_date]).filter(payment__payment_status='Completed').order_by('order_date')
    except:
        pass
    rows = order_data.values_list(
        'id','order_customer','order_date','payment__total_amount','payment__payment_method'
    )
    

    for row in rows:
        row_num = row_num + 1

        for col_num in range(len(columns)):
             ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)

    return response


@never_cache
def export_pdf(request):
    pass
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.datetime.now())+'.pdf'

    # response["Content-Transfer-Encoding"] = 'binary'

    # html_string = render_to_string('pdf_output' , {'report':[], 'total' : 0})
    # html = HTML(string=html_string)
    # result = html.write_pdf()

    # with tempfile.NamedTemporaryFile(delete=True) as output :
    #     output.write(result)
    #     output.flush()

    #     output = open(output.name, 'rb')
    #     response.write(output.read())
    # return response

@never_cache
def admin_login(request):
    if request.session.has_key('session_name'):
        return redirect('admin_home')
    if request.method == 'GET':
        return render(request, 'admin_login.html')
    else :
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username= username , password = password)
        if user is not None :
            user_is = CustomUser.objects.get(username = username)
            if user_is.is_superuser == True:
                login(request, user)
                return redirect('admin_home')
            else:
                messages.error(request,"You have no access to admin page")
        else:
            messages.error(request,"Incorrect UserName or Password")
    return redirect('admin_login')


@never_cache
def admin_logout(request):
    logout(request)
    return redirect("admin_login")

##################user_management###############################

def block_user(request):
    id = request.GET.get('id')
    i= CustomUser.objects.get(pk = id)
    if i.blocked == True :
        i.blocked = False
    else :
        i.blocked = True
    i.save()
    status = i.blocked
    print(status)
    response = {'status' : status}
    return JsonResponse(response)






@never_cache
@login_required(login_url='/iamadmin/')
def users_table(request):
    page = 'userpage'
    user_list = CustomUser.objects.all().exclude(phone_number = None)
    p = Paginator(user_list, 5)
    pg = request.GET.get('pg')
    user_list = p.get_page(pg)
    context = {'user_list': user_list,'page': page,}
    return render(request,'users_table.html',context)


@login_required(login_url='/iamadmin/')
@never_cache
def categories_table(request):
    page = 'categorypage'
    context = {'categories': Categorie.objects.all(),'page': page}
    return render(request,'categories_table.html',context)

@login_required(login_url='/iamadmin/')
@never_cache
def brand_table(request):
    page = 'brandpage'
    context = {'brands': Brand.objects.all(),'page': page}
    return render(request,'brands.html',context)

@never_cache
@login_required(login_url='/iamadmin/')
def products_table(request):
    page = 'productpage'
    products = Product.objects.all()
    p = Paginator(products, 5)
    pg = request.GET.get('pg')
    products = p.get_page(pg)
    context = {'products': products,'page': page}
    return render(request,'products_table.html',context)



@never_cache
@login_required(login_url='/iamadmin/')
def order_table(request):
    page = 'orderpage'
    orderdetails = Orderdetail.objects.all().exclude(order_status='Cart').exclude(order_status='Gobuy').order_by('-payment')
    p = Paginator(orderdetails, 5)
    pg = request.GET.get('pg')
    orderdetails = p.get_page(pg)
    context = {'orderdetails' : orderdetails,'page': page,}

    return render(request,'order_table.html',context)


@never_cache
@login_required(login_url='/iamadmin/')
def banner_table(request):
    page = 'bannerpage'
    banners = Banner.objects.all()

    context = {'banners' : banners,'page': page,}

    return render(request,'banner_table.html',context)

@never_cache
@login_required(login_url='/iamadmin/')
def coupon_table(request):
    page = 'couponcreatepage'
    coupons = CouponDetail.objects.all()
    today = date.today()
    print(today)
    context = {'coupons' : coupons ,'date' : today,'page':page}
    return render(request,'coupon_table.html',context)





##################   coupon_management    ###############################

@never_cache
@login_required(login_url='/iamadmin/')
def coupon_usage(request):
    page = 'couponusepage'
    coupons = UseCoupon.objects.exclude(used = False)
    context = {'coupons' : coupons ,'page': page,}
    return render(request,'coupon_usage.html',context)

@login_required(login_url='/iamadmin/')
@never_cache
def coupon_add(request):
    users = CustomUser.objects.all()
    form = Coupon_form()
    if request.method == 'POST' :
        form = Coupon_form(request.POST, request.FILES)
        exp_date = request.POST.get('exp-date')
        
        print(exp_date)
        if form.is_valid():
            instance = form.save(commit=False)
            if exp_date != '' and exp_date != None :
                instance.exp_date = exp_date
            instance.save()
            coupon = CouponDetail.objects.get(id=instance.id)
            for user in users:
                UseCoupon.objects.create(user = user,coupon = coupon)
            return redirect('coupon_table')
    context = {'form' : form}
    return render(request, 'coupon_form.html', context)




def coupon_status(request):
    id = request.GET.get('id')
    coupon = CouponDetail.objects.get(id = id)
    if coupon.active == True:
        coupon.active = False
    else:
        coupon.active = True
    coupon.save()
    status = coupon.active 
    response = {'status' : status}
    return JsonResponse(response)



##################banner_management###############################

@login_required(login_url='/iamadmin/')
@never_cache
def banner_add(request):
    form = banner_form()
    if request.method == 'POST' :
        form = banner_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('banner_table')
    context = {'form' : form}
    return render(request, 'banner_form.html', context)


@login_required(login_url='/iamadmin/')
def banner_update(request, id):
    form = banner_form()
    if request.method == 'POST' :
        i = Banner.objects.get(pk = id)
        form = banner_form(request.POST, request.FILES, instance = i)
        if form.is_valid():
            print('Banner')
            form.save()
            return redirect('banner_table')
    else :
        i= Banner.objects.get(pk = id)
        form = banner_form( instance = i)
    context = {'form' : form}
    return render(request, 'banner_form.html', context)


@login_required(login_url='/iamadmin/')
def banner_delete(request):
    id  = request.GET.get('id')
    i = Banner.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)   
    



##################categories_management###############################

@never_cache
@login_required(login_url='/iamadmin/')
def categories_add(request):
    form = Categories_form()
    if request.method == 'POST' :
        form =  Categories_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories_table')
    context = {'form' : form}
    return render(request, 'categories_form.html', context)



@login_required(login_url='/iamadmin/')
def categories_update(request, id):
    form = Categories_form()
    if request.method == 'POST' :
        i = Categorie.objects.get(pk = id)
        form = Categories_form(request.POST, instance = i)
        if form.is_valid():
            form.save()
            return redirect('categories_table')
    else :
        i= Categorie.objects.get(pk = id)
        form = Categories_form( instance = i)
    context = {'form' : form}
    return render(request, 'categories_form.html', context)


@login_required(login_url='/iamadmin/')
def categories_delete(request):
    id  = request.GET.get('id')
    i = Categorie.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)
    

##################brands_management###############################

@never_cache
@login_required(login_url='/iamadmin/')
def brand_add(request):
    form = Brand_form()
    if request.method == 'POST' :
        form =  Brand_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('brand_table')
    context = {'form' : form}
    return render(request, 'brand_form.html', context)



@login_required(login_url='/iamadmin/')
def brand_update(request, id):
    form = Brand_form()
    if request.method == 'POST' :
        i = Brand.objects.get(pk = id)
        form = Brand_form(request.POST, instance = i)
        if form.is_valid():
            form.save()
            return redirect('brand_table')
    else :
        i= Brand.objects.get(pk = id)
        form = Brand_form( instance = i)
    context = {'form' : form}
    return render(request, 'brand_form.html', context)


@login_required(login_url='/iamadmin/')
def brand_delete(request):
    id  = request.GET.get('id')
    i = Brand.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)
    

##############product_management####################################


@login_required(login_url='/iamadmin/')
def product_view(request, id):
    product = Product.objects.get(pk = id)
    context = {'product' : product}
    return render(request, 'showsingleproduct.html', context)


@login_required(login_url='/iamadmin/')
@never_cache
def products_add(request):
    form = products_form()
    if request.method == 'POST' :
        form = products_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('products_table')
    context = {'form' : form}
    return render(request, 'products_form.html', context)


@login_required(login_url='/iamadmin/')
def products_update(request, id):
    form = products_form()
    if request.method == 'POST' :
        i = Product.objects.get(pk = id)
        form = products_form(request.POST, request.FILES, instance = i)
        if form.is_valid():
            form.save()
            return redirect('products_table')
    else :
        i= Product.objects.get(pk = id)
        form = products_form( instance = i)
    context = {'form' : form}
    return render(request, 'products_form.html', context)


@login_required(login_url='/iamadmin/')
def products_delete(request):
    id  = request.GET.get('id')
    i = Product.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)  
 
############order_management#######################################


@login_required(login_url='/iamadmin/')
def order_products(request, id):
    order, created = Orderdetail.objects.get_or_create(id = id)
    items = order.orderitem_set.all()
    context = { 'order':order , 'items': items, }
    return render(request,'order_products.html', context)


@login_required(login_url='/iamadmin/')
def order_cancel(request, id):
    order = Orderdetail.objects.get(id = id)
    items = OrderItem.objects.filter(item_order = order)
    order.order_status = 'Cancelled'
    for item in items :
            ordered_items = item.item_quantity
            current_stock = item.item_product.quantity_available
            new_stock = current_stock + ordered_items
            product_id = item.item_product.id
            Product.objects.filter(id = product_id).update(quantity_available = new_stock)
    order.save()
    return redirect('order_table')

@login_required(login_url='/iamadmin/')
def update_order(request, id):
    order = Orderdetail.objects.get(id = id)
    context = {'order': order}
    return render(request,'update_order.html',context)

@login_required(login_url='/iamadmin/')
def order_shipped(request, id):
    order = Orderdetail.objects.get(id = id)
    updated = 'Shipped'
    order.order_status = updated
    order.save()
    return redirect ('order_table')

@login_required(login_url='/iamadmin/')
def order_ood(request, id):
    order = Orderdetail.objects.get(id = id)
    updated = 'Out Of Delevery'
    order.order_status = updated
    order.save()
    return redirect ('order_table')


@login_required(login_url='/iamadmin/')
def order_completed(request, id):
    order = Orderdetail.objects.get(id = id)
    form = OrderUpdation()
    updated = 'Completed'    
    payobj = Payment.objects.get(order = order)
    transaction_id = datetime.datetime.now().timestamp()
    payobj.transaction_id = transaction_id
    payobj.payment_status = 'Completed'
    payobj.save()
    order.order_status = updated
    order.save()
    return redirect ('order_table')
    


def cancel_req(request, id):
    pass


##################  offer management  ###############################


def category_offers(request):
    page = 'categoryofferpage'
    offers = CategoryOffer.objects.all()
    context = {'offers': offers,'page': page}
    return render(request,'categoryoffers.html',context)


@never_cache
@login_required(login_url='/iamadmin/')
def categories_offers_add(request):
    page = 'cat_offer'
    form = Categorieoffers_form()
    if request.method == 'POST' :
        form =  Categorieoffers_form(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save()
            id = offer.id
            return redirect('show_offer_category',id)
    context = {'form' : form, 'page': page,}
    return render(request, 'offers_form.html', context)



@login_required(login_url='/iamadmin/')
def categories_offer_update(request, id):
    page = 'cat_offer'
    form = Categorieoffers_form()
    if request.method == 'POST' :
        i = CategoryOffer.objects.get(pk = id)
        form = Categorieoffers_form(request.POST, instance = i)
        if form.is_valid():
            offer = form.save()
            id = offer.id
            return redirect('show_offer_category',id)
    else :
        i= CategoryOffer.objects.get(pk = id)
        form = Categorieoffers_form( instance = i)
    context = {'form' : form, 'page': page,}
    return render(request, 'offers_form.html', context)


@login_required(login_url='/iamadmin/')
def show_offer_category(request, id):
    included_categories = Categorie.objects.filter(c_offer = id)
    excluded_categories = Categorie.objects.exclude(c_offer = id)
    context = {'categories': included_categories, 'add_categories': excluded_categories,'offer':id}
    return render(request, 'showoffercategories.html', context)


@login_required(login_url='/iamadmin/')
def remove_offer_category(request):
    id  = request.GET.get('id')
    i = Categorie.objects.get(pk = id)
    i.c_offer = None
    i.save()
    context = {'form' : "form"}
    return JsonResponse(context)

@login_required(login_url='/iamadmin/')
def add_offer_category(request):
    id  = request.GET.get('id')
    offer_id = request.GET.get('offer')
    offer = CategoryOffer.objects.get(pk = offer_id)
    i = Categorie.objects.get(pk = id)
    i.c_offer = offer
    i.save()
    context = {'form' : "form"}
    return JsonResponse(context)



@login_required(login_url='/iamadmin/')
def categories_offer_delete(request):
    id  = request.GET.get('id')
    i = CategoryOffer.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)
    


def product_offers(request):
    page = 'productofferpage'
    offers = ProductOffer.objects.all()
    context = {'offers': offers,'page': page}
    return render(request,'productoffers.html',context)



@never_cache
@login_required(login_url='/iamadmin/')
def product_offer_add(request):
    page = 'pro_offer'
    form = Productoffers_form()
    if request.method == 'POST' :
        form =  Productoffers_form(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save()
            id = offer.id
            return redirect('show_offer_products',id)
    context = {'form' : form, 'page': page,}
    return render(request, 'offers_form.html', context)



@login_required(login_url='/iamadmin/')
def product_offer_update(request, id):
    page = 'pro_offer'
    form = Productoffers_form()
    if request.method == 'POST' :
        i = ProductOffer.objects.get(pk = id)
        form = Productoffers_form(request.POST, instance = i)
        if form.is_valid():
            offer = form.save()
            id = offer.id
            return redirect('show_offer_products',id)
    else :
        i= ProductOffer.objects.get(pk = id)
        form = Productoffers_form( instance = i)
    context = {'form' : form, 'page': page,}
    return render(request, 'offers_form.html', context)


@login_required(login_url='/iamadmin/')
def show_offer_products(request, id):
    included_products = Product.objects.filter(p_offer = id)
    excluded_products = Product.objects.exclude(p_offer = id)
    context = {'products': included_products, 'add_products': excluded_products,'offer':id}
    return render(request, 'showofferproducts.html', context)


@login_required(login_url='/iamadmin/')
def remove_offer_product(request):
    id  = request.GET.get('id')
    i = Product.objects.get(pk = id)
    i.p_offer = None
    i.save()
    context = {'form' : "form"}
    return JsonResponse(context)

@login_required(login_url='/iamadmin/')
def add_offer_product(request):
    id  = request.GET.get('id')
    offer_id = request.GET.get('offer')
    print(offer_id)
    offer = ProductOffer.objects.get(pk = offer_id)
    i = Product.objects.get(pk = id)
    i.p_offer = offer
    i.save()
    context = {'form' : "form"}
    return JsonResponse(context)


@login_required(login_url='/iamadmin/')
def product_offer_delete(request):
    id  = request.GET.get('id')
    i = ProductOffer.objects.get(pk = id)
    i.delete()
    context = {'form' : "form"}
    return JsonResponse(context)
