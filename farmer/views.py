from django.shortcuts import render,redirect
from django.http import HttpResponse
import json
from newsapi import NewsApiClient
import requests
import ast
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import AddProduct
from shop.models import Product,Rating
from django.views.generic import CreateView
from accounts.models import User,Farmer
from django.contrib.auth.decorators import login_required


from django.contrib import messages
from django.contrib.auth import login,logout,authenticate

# Create your views here.
def index(request):
    return render(request,"farmer/index.html")

def about(request):
    return render(request,"farmer/about.html")

def news(request):
    newsapi = NewsApiClient(api_key='310e66acf0d04b249b67b50c07779f7b')
    top_headlines = newsapi.get_everything(q='farmer'or'crop')
    return render(request,"farmer/news.html",{"news":top_headlines})

def tutorials(request):
    return render(request,"farmer/tutorials.html")

def cropinfo(request):
    return render(request,"farmer/cropinfo.html")

def contact(request):
    return render(request,"farmer/contact.html")

def dashboard(request):
    prod=request.POST.get('commodity')
    state=request.POST.get('state')
    if state!=None and prod!=None:
        r=requests.get('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json&offset=0&filters[commodity]='+prod+'&filters[state]='+state)
        r=r.json()
        print(prod)
        print(state)
        return render(request,"farmer/dashboard.html",{'data':r})
    else:
        return render(request,"farmer/dashboard.html",{'data':''})

def handlelogin(request):
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']
        user=authenticate(username=loginusername,password=loginpassword)

        if user is not None and user.is_farmer:
            login(request,user)
            messages.success(request,"Successfully Logged In")
            return render(request,"farmer/index.html")
        else:
            messages.error(request,"Invalid Credentials")
            return render(request,"farmer/login.html")

    else:
        return render(request, "farmer/login.html")

def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully Logged Out")
    return redirect('/')


def signup(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        confirmPassword=request.POST['confirmPassword']
        if len(username) > 15:
            messages.error(request, "Username must be under 10 characters")
            return redirect('/')
        if password != confirmPassword:
            messages.error(request, "Passwords do not match")
            return redirect('/')
        if password == confirmPassword:
            user = User.objects.create_user(username,email,password)
            user.is_farmer = True
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            farmer = Farmer.objects.create(user=user)
            farmer.phoneNumber=request.POST['phoneNumber']
            farmer.cardNumber = request.POST['cardNumber']
            farmer.email = request.POST['email']
            farmer.state = request.POST['state']
            farmer.village = request.POST['village']
            farmer.zip = request.POST['zip'] 
            farmer.save()
            messages.success(request,"Your account has been successfully created!!!!")
            return render(request,'farmer/login.html')
    else:
        return render(request, "farmer/signup.html")


def cropdisease(request):
    return render(request, "farmer/cropdisease.html")

def fullnews(request):
    return render(request, "farmer/fullnews.html")


@login_required(login_url="../farmer/login")
def addproduct(request):
    if request.method=="POST":
        print(request)
        category=request.POST.get('category',"")
        subcategory=request.POST.get('subcategory',"")
        variety=request.POST.get('variety',"")
        location=request.POST.get('location',"")
        quantity=request.POST.get('quantity')
        price=request.POST.get('price')
        date=request.POST.get('date')
        myfile = request.POST.get('myfile')
        aln=request.POST.get('aln')
        temp=Farmer.objects.get(user=request.user)
        addprod=AddProduct(category=category,sub_category=subcategory,variety=variety,location=location,quantity=quantity,price=price,pub_date=date,image=myfile,aln=aln,farmer=temp)
        addprod.save()
        product_name=subcategory+'-'+variety
        temp=Farmer.objects.get(user=request.user)
        a=Product.objects.filter(product_name=product_name,farmer=temp)
        #print(a[0].quantity)
        if len(a)==0:
            prod=Product(product_name=product_name,category=category,sub_category=subcategory,variety=variety,location=location,quantity=quantity,price=price,pub_date=date,image=myfile,farmer=temp)
            prod.save()
            print("id: ",prod.product_id)
        else:
            a[0].quantity += int(quantity)
            a[0].price = price
            a[0].pub_date = date
            a[0].image = myfile
            a[0].save()
        #print(a)
        #print(type(a))
        print(temp)
        #temp=temp.username
        #print(temp)
        a=Rating.objects.filter(product_name=product_name,farmer=temp)

        if len(a)==0:
            rating=Rating(product_name=product_name,farmer=temp,ratings=0)
            rating.save()
        messages.success(request,"Your product has been successfully added!")
        return render(request, "farmer/index.html")
    return render(request, "farmer/addproduct.html")

def StatewiseProductPrice(request):
    return render(request, "farmer/StatewiseProductPrice.html")



def cropDiseasePrediction(request):
    return render(request, "farmer/cropDiseasePrediction.html")

