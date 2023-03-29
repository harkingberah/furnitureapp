from django.contrib import admin
# from .models import AppInfo
from .models import *

# Register your models here.


#we need to push the model into the database where all the files will be
#as an admin, you need to create your super login details(super user)
# py manage.py createsuperuser
#type in a password, it will not show. but note that it's actually writing your password.
#email is optional
class AppInfoAdmin(admin.ModelAdmin):
    list_display=('appname','copyright')
    
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    list_display= ['id', 'category', 'name', 'price', 'uploaded', 'edited']
class ContactAdmin(admin.ModelAdmin):
    list_display= ['id', 'full_name', 'sent']
class CartAdmin(admin.ModelAdmin):
    list_display= ['id', 'user', 'furniture','price','amount','paid']
class PaymentAdmin(admin.ModelAdmin):
    list_display= ['id', 'user', 'first_name','amount','paid','purchase_date'] 
    # you can add last name if you want
    

admin.site.register(AppInfo)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Customer)
admin.site.register(Cart, CartAdmin)
admin.site.register(Payment, PaymentAdmin)


