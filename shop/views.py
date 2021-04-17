from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
import json
from .models import Product,Contact,Order,OrderUpdate,Rating
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from newsapi import NewsApiClient
from django.db.models import Count
from django.core.mail import send_mail
import stripe # new
from django.conf import settings # new
from django.views.generic.base import TemplateView
from django.contrib import messages
from accounts.models import User,Customer,Farmer
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required


stripe.api_key = settings.STRIPE_SECRET_KEY # new
stripe.pub_key=settings.STRIPE_PUBLISHABLE_KEY


# Create your views here.
def index(request):
    allProds=[]
    catProds=Product.objects.values('category','id','sub_category')
    cats={item['category'] for item in catProds}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        majorlst=[]
        templst=[]
        for i in prod:
            if i.sub_category not in templst:
                templst.append(i.sub_category)
                majorlst.append(i)
        n=len(majorlst)
        nSlides=n//4+ceil((n/4)-(n//4))
        allProds.append([majorlst,range(1,nSlides),nSlides])
    params={'allProds':allProds}
    return render(request,"shop/index.html",params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query.lower() in item.sub_category.lower() or query in item.variety.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    print(query)
    allProds = []
    catprods = Product.objects.values('category', 'id','sub_category')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request,"shop/about.html")

def news(request):
    newsapi = NewsApiClient(api_key='310e66acf0d04b249b67b50c07779f7b')
    top_headlines = newsapi.get_everything(q='farmer'or'crop')
    return render(request,"shop/news.html",{"news":top_headlines})

def contact(request):
    thank=False
    if request.method=="POST":
        print(request)
        name=request.POST.get('name',"")
        phone=request.POST.get('phone',"")
        email=request.POST.get('email',"")
        subject=request.POST.get('subject',"")
        desc=request.POST.get('text',"")
        contact=Contact(name=name,phone=phone,email=email,subject=subject,desc=desc)
        contact.save()
        thank=True
    return render(request,"shop/contact.html",{"thank":thank})

@login_required(login_url="../shop/login")
def tracker(request):
    if request.method == 'POST':
        orderId=request.POST.get('orderId',"")
        email=request.POST.get('email',"")
        #return HttpResponse(f'{orderId} and {email}')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc, 'time':item.timestamp})
                    response = json.dumps(updates, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request,"shop/tracker.html")

def productview(request,myid):
    product=Product.objects.filter(sub_category=myid)
    print(len(product))
    list1=[]
    for i in range(len(product)):
        prod={}
        prod['farmer']=product[i].farmer
        farmer=product[i].farmer
        product_name=product[i].product_name
        rating=Rating.objects.filter(product_name=product_name,farmer=farmer)
        prod['product_name']=product[i].product_name
        prod['id']=product[i].id
        prod['rating']=rating[0].ratings
        prod['category']=product[i].category
        prod['sub_category']=product[i].sub_category
        prod['variety']=product[i].variety
        prod['location']=product[i].location
        prod['quantity']=product[i].quantity
        prod['price']=product[i].price
        prod['image']=product[i].image
        print(type(prod['rating']))
        list1.append(prod)  
    print(list1)
    forid=Product.objects.values('id')
    print(forid)
    return render(request,"shop/prodview.html",{'list1':list1,'id':forid})

@login_required(login_url="../shop/login")
def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', "")
        name=request.POST.get('name',"")
        amount=request.POST.get('amount',0)
        phone=request.POST.get('phone',"")
        email=request.POST.get('email',"")
        addr=request.POST.get('address',"")
        addr2 = request.POST.get('address2', "")
        city=request.POST.get('city',"")
        state = request.POST.get('state', "")
        zip = request.POST.get('zip', "")
        temp = Customer.objects.get(user=request.user)
        orders=Order(name=name,amount=amount,phone=phone,email=email,address=addr+addr2,city=city,state=state,zip_code=zip,items_json=items_json,customer=temp)
        orders.save()
        update=OrderUpdate(order_id=orders.order_id,update_desc="Your order has been placed",customer=temp)
        update.save()
        id=orders.order_id
        print(items_json)
        print(amount)
        
        send_mail("Krishi setu!", "Thanks for ordering!",
          "krishi setu <krishisetu0@gmail.com>", [email])
        #return render(request,"shop/payment.html",{'amount':amount,'items_json':items_json})
        return HttpResponseRedirect('payment')
    return render(request,"shop/checkout.html")


class HomePageView(TemplateView):
    template_name = 'shop/payment.html'

    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

@login_required(login_url="../shop/login")
def charge(request):
    if request.method == 'POST':
        amt=list(Order.objects.values('amount').last().values())
        email=list(Order.objects.values('email').last().values())
        order_id=list(Order.objects.values('order_id').last().values())
        order_id=order_id[0]
        order=Order.objects.filter(order_id=order_id)
        items_json=order[0].items_json
        dct=json.loads(items_json)
        for k,v in dct.items():
            quantity=v[0]
            id=int(v[3])
            prod=Product.objects.filter(id=id)
            old_quantity=prod[0].quantity
            Product.objects.filter(id=id).update(quantity=old_quantity-quantity)        
        charge = stripe.Charge.create(
            amount=amt[0]*100,
            currency='inr',
            description=email[0],
            source=request.POST['stripeToken']
        )
        
    return render(request, "shop/charge.html")

def handlelogin(request):
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']
        user=authenticate(username=loginusername,password=loginpassword)

        if user is not None and user.is_customer:
            login(request,user)
            messages.success(request,"Successfully Logged In")
            return redirect("/shop")

        else:
            messages.error(request,"Invalid Credentials")
            return render(request,"shop/login.html")

    else:
        return render(request, "shop/login.html")

def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully Logged Out")
    return redirect('/')

def signup(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        confirmPassword = request.POST['confirmPassword']
        if len(username) > 15:
            messages.error(request, "Username must be under 10 characters")
            return redirect('/')
        if password != confirmPassword:
            messages.error(request, "Passwords do not match")
            return redirect('/')
        if password == confirmPassword:
            user = User.objects.create_user(username,email,password)
            user.is_customer=True
            user.first_name=request.POST['fname']
            user.last_name=request.POST['lname']
            user.save()
            customer = Customer.objects.create(user=user)
            customer.email=request.POST['email']
            customer.fssai=request.POST['fssaino']
            customer.save()
            messages.success(request, "Your account has been successfully created!!!!")
            return render(request, 'shop/login.html')

    else:
        return render(request, "shop/signup.html")

@login_required(login_url="../shop/login")
def history(request):
    temp=Customer.objects.get(user=request.user)
    order=Order.objects.filter(customer=temp)
    params = {'order': order}
    return render(request,'shop/history.html',params)

def orderdetail(request,myid):
    order=Order.objects.filter(order_id=myid)
    temp=order[0].items_json
    dct=json.loads(temp)
    print(type(dct))
    
    print(dct)
    lst=[]
    for key,values in dct.items():
        lst.append(values)
    print(lst)
    params = {'order': order,'lst':lst}
    return render(request,'shop/orderdetail.html',params)


def rating(request,myid):
    print(myid)
    prod=Product.objects.filter(id=myid)
    product_name=prod[0].product_name
    farmer=prod[0].farmer
    params={'prod':prod}
    rating=Rating.objects.filter(product_name=product_name,farmer=farmer)
    if request.method=="POST":
        rate=request.POST.get('rating',0)
        rate=int(rate)
        if rating[0].ratings==0:
            Rating.objects.filter(product_name=product_name,farmer=farmer).update(ratings=rate)
            print(rating[0].ratings)
        else:
             Rating.objects.filter(product_name=product_name,farmer=farmer).update(ratings=(rating[0].ratings+rate)//2)
             print(rating[0].ratings)

    return render(request,'shop/rating.html',params)

'''def productview(request,myid):
    product=Product.objects.filter(sub_category=myid)
    forid=Product.objects.values('id')
    print(forid)
    return render(request,"shop/prodview.html",{'product':product,'id':forid})'''