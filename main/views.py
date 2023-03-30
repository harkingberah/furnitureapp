import requests
import uuid
import json
from django.shortcuts import render, redirect
# from .models import AppInfo, Category, Product
from django.contrib import messages
from django.db.models import Q 
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from .models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from .forms import ContactForm, CustomerForm
from .forms import *



def homepage(request):
    info=AppInfo.objects.get(pk=1)
    fdog = Category.objects.all()
    featured = Product.objects.filter(featured=True)
#     Category=Category.objects.all()

    context = {
        'info': info,
        'fdog': fdog,
        'featured': featured
      #   'Category':Category
    }
    return render(request, 'index.html', context)

def products(request):
    allprod = Product.objects.all()
    p = Paginator(allprod, 8)
    page = request.GET.get('page')
    pagin = p.get_page(page)

    context = {
        'pagin': pagin
    }

    return render(request, 'product.html', context)

def category(request, id, slug):
      categ=Category.objects.get(pk=id)
      catprod=Product.objects.filter(category_id=id)
      
      context={
            'categ': categ,
            'catprod':catprod
      }
      return render(request, 'category.html', context)

def detail(request, id, slug):
      detail=Product.objects.get(pk=id)
      
      context={
            'detail': detail
      }
      
      return render(request, 'detail.html', context)
  
def contact(request):
    contact=ContactForm()
    if request.method=='POST':
        contact=ContactForm(request.POST)
        if contact.is_valid():
            contact.save()
            messages.success(request, 'your message is sent successfully')
            return redirect('home')
    return render(request, 'contact.html')

def signout(request):
    logout(request)
    messages.success(request,'you are now signed out')
    return redirect('signin')

def signin(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user= authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'login successful')
            return redirect('home')
        else:
            messages.error(request, 'username/password is incorrect')
            return redirect('signin')
    return render(request, 'login.html')
            
def register(request):
    form =CustomerForm()
    if request.method == 'POST':
        phone=request.POST['phone']
        address=request.POST['address']
        pix=request.POST['pix']
        form = CustomerForm(request.POST)
        if form.is_valid():
            user =form.save()
            newuser= Customer(user=user)
            newuser.first_name= user.first_name
            newuser.last_name=user.last_name
            newuser.email=user.email
            newuser.phone=phone
            newuser.address=address
            newuser.pix=pix
            newuser.save()
            messages.success(request, f'dear {user.username} your account is created successfully')
            return redirect('signin')
        else:
            messages.error(request, form.errors)
            return redirect('signup')
        
    return render(request, 'signup.html')
            
        
def search(request):
    if request.method == 'POST':
        item = request.POST['search']
        search = Q(name__icontains=item) | Q(price__icontains=item) | Q(description__icontains=item)
        searched_item = Product.objects.filter(search)
        context = {
            'item': item,
            'searched_item': searched_item
        }
        return render(request, 'search.html', context)
@login_required(login_url="signin")
def profile(request):
    userprof=Customer.objects.get(user__username = request.user.username)
    
    context={
        'userprof':userprof
    }
    
    return render(request,'profile.html', context)

def profile_update(request):
    userprof=Customer.objects.get(user__username =request.user.username)
    form = ProfileUpdateForm(instance=request.user.customer)
    if request.method=='POST':
        form=ProfileUpdateForm(request.POST, request.FILES, instance=request.user.customer)
        if form.is_valid():
            user= form.save()
            new=user.first_name.title()
            messages.success(request, f'Dear {new}, your profile has been updated successfully.')
            return redirect('profile')
        else:
            new=user.first_name.title()
            messages.error(request, f'Error updating profile for {new}. Please check the form data and try again.')           
            return redirect('profile_update')
        
    context={
        'userprof':userprof
    }
    return render(request, 'profile_update.html', context)
@login_required(login_url="signin")
def password_update(request):
    userprof=Customer.objects.get(user__username=request.user.username)
    passupdate=PasswordChangeForm(request.user)
    if request.method=='POST':
        new=request.user.username.title()
        passupdate=PasswordChangeForm(request.user, request.POST)
        if passupdate.is_valid():
            user=passupdate.save()
            update_session_auth_hash(request, user)
            messages.success(request, f"Dear {new}, your password change is successful.")
            return redirect('profile')
        else:
            messages.error(request, f"Dear {new}, a problem occurred with the following errors: {passupdate.errors}")
            return redirect('password_update')
    context={
        'userprof': userprof,
        'passupdate': passupdate
    }
    return render(request, 'password_update.html', context)
@login_required(login_url="signin")
def add_to_cart(request):
    if request.method =='POST':
        quantity = int(request.POST['quantity'])
        furniture=request.POST['productid']
        main=Product.objects.get(pk=furniture)
        cart = Cart.objects.filter(user__username=request.user.username, paid=False)
        if cart:
            basket=Cart.objects.filter(user__username=request.user.username, paid=False, furniture=main.id, quantity=quantity).first()
            if basket:
                basket.quantity += quantity
                basket.amount =main.price * basket.quantity
                basket.save()
                messages.success(request, 'one item added to cart')
                return redirect('products')
            else:
                newitem=Cart()
                newitem.user =request.user
                newitem.furniture =main
                newitem.quantity =quantity
                newitem.price=main.price
                newitem.amount = main.price * quantity
                newitem.paid=False
                newitem.save()
                messages.success(request, 'one item added to cart')
                return redirect('products')
        else:
                newcart=Cart()
                newcart.user =request.user
                newcart.furniture =main
                newcart.quantity =quantity
                newcart.price = main.price
                newcart.amount=main.price * quantity
                newcart.paid=False

                newcart.save()
                messages.success(request, 'one item added to cart')
                return redirect('products')
@login_required(login_url="signin")
def cart(request):
    cart=Cart.objects.filter(user__username = request.user.username, paid=False)
    for item in cart:
        item.amount = float(item.price * item.quantity)
        item.save()
        
    subtotal= 0
    vat= 0
    total =0
    
    for item in cart:
        subtotal+=item.amount
        vat =0.075 * subtotal
        total =vat + subtotal
            
    context={
        'cart': cart,
        'subtotal':subtotal,
        'vat': vat,
        'total': total,
    }
    return render(request, 'cart.html',context)

def update(request):
    if request.method=='POST':
        fprod = request.POST['productid']
        quant= request.POST['quant']
        newqty =Cart.objects.get(pk=fprod)
        newqty.quantity= quant
        newqty.amount = int(newqty.price) * newqty.quantity
        newqty.save()
        messages.success(request, 'quantity updated')
        return redirect('cart')
    
def delete(request):
    if request.method =='POST':
        delitem = request.POST['delid']
        Cart.objects.filter(pk=delitem).delete()
        messages.success(request, 'one item deleted from cart')
        return redirect('cart')

def checkout(request):
    userprof= Customer.objects.get(user__username = request.user.username)
    cart=Cart.objects.filter(user__username = request.user.username, paid=False)
    for item in cart:
        item.amount = float(item.price * item.quantity)
        item.save()
        
    subtotal= 0
    vat= 0
    total =0
    
    for item in cart:
        subtotal+=item.amount
        vat =0.075 * subtotal
        total =vat + subtotal
            
    context={
        'userprof': userprof,
        'cart': cart,
        'subtotal':subtotal,
        'vat': vat,
        'total': total,
    }
    return render(request, 'checkout.html',context)

@login_required(login_url="signin")
def payment(request):
    if request.method == 'POST':
        profile = Customer.objects.get(user__username=request.user.username)
        api_key = 'sk_test_db4d6edb1fdca6fdcf896e2264d97d18eb6db3b6' #secret key from paystack
        curl = 'https://api.paystack.co/transaction/initialize' #paystack call url
        cburl = 'http://16.16.77.142/callback' #payment confirmation page
        ref = str(uuid.uuid4()) # reference id required by paystack as an additional reference number
        order_no = profile.id
        total = float(request.POST['total']) * 100 #total amount to be charged from customer card
        user = User.objects.get(username=request.user.username) #query the model for customer details
        email = user.email
        first_name = request.POST['first_name'] # collect data from template
        last_name = request.POST['last_name'] # collect data from template
        address = request.POST['address'] # collect data from template
        phone = request.POST['phone'] # collect data from template

        #collect data to send to paystack via call url
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference': ref, 'amount': int(total), 'email': email, 'callback_url': cburl, 'order_number': order_no, 'currency': 'NGN'}

        #MAKE A CALL TO PAYSTACK
        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, 'network busy, try again later')
        else:
            transback = json.loads(r.text)
            rdurl = transback['data']['authorization_url']
            
            account = Payment()
            account.user = user
            account.first_name = first_name
            account.last_name = last_name
            account.amount = total/100
            account.paid = True
            account.pay_code = ref
            account.phone = phone
            account.address=address
            account.save()

            return redirect(rdurl)

    return redirect('checkout')       
@login_required(login_url="signin")
def callback(request):
    userprof=Customer.objects.get(user__username = request.user.username)
    cart = Cart.objects.filter(user__username = request.user.username, paid=False)
    
    for item in cart:
        item.paid =True
        item.save()
        
        furniture =Product.objects.get(pk=item.furniture.id)
        
    context = {
        'userprof': userprof,
        'cart': cart,
        'furniture':furniture,
    }    
    return render(request, 'callback.html', context)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        