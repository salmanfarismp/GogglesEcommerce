from django.contrib import admin

from userapp.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Categorie)
admin.site.register(OrderItem)
admin.site.register(Orderdetail)
admin.site.register(ShippingAddress)
admin.site.register(Payment)
admin.site.register(Banner)
admin.site.register(Brand)
admin.site.register(CouponDetail)
admin.site.register(UseCoupon)
admin.site.register(ProductOffer)
admin.site.register(CategoryOffer)
admin.site.register(WishlistItem)