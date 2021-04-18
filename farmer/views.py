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

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
from PIL import Image
from tensorflow.keras.models import Sequential
import numpy as np
from glob import glob
from tensorflow.keras.models import load_model



model=load_model('./model_resnet50.h5')


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
    content = ""
    a = ""
   
    print(request.method)
    if (request.method == 'POST'):
        name = request.POST['name']
        print(name)
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        testimage='.'+uploaded_file_url
        
        img = image.load_img(testimage, target_size=(224,224))

        # Preprocessing the image
        x = image.img_to_array(img)
        # x = np.true_divide(x, 255)
        ## Scaling
        x=x/255
        x = np.expand_dims(x, axis=0)
        preds = model.predict(x)
        
        preds=np.argmax(preds, axis=1)
        print(preds)
        if preds==0:
            preds="Tomato___Bacterial_spot"
            a = "Prevention and treatment"
            content = "Only use certified disease-free seed and plants. Avoid areas that were planted with peppers or tomatoes during the previous year. Avoid overhead watering by using drip or furrow irrigation. Remove all diseased plant material. Prune plants to promote air circulation. Spraying with a copper fungicide will give fairly good control the bacterial disease."
            
        elif preds==1:
            preds="Tomato___Early_blight"
            a = "Prevention and treatment"
            content = "Use resistant or tolerant tomato cultivars. Use pathogen-free seed and do not set diseased plants in the field. Use crop rotation, eradicate weeds and volunteer tomato plants, space plants to not touch, mulch plants, fertilize properly, don’t wet tomato plants with irrigation water, and keep the plants growing vigorously. Trim off and dispose of infected lower branches and leaves."
            

        elif preds==2:
            preds="Tomato__Late_blight"
            a = "Prevention and treatment"
            content = "The following guidelines should be followed to minimize late blight problems: Keep foliage dry. Locate your garden where it will receive morning sun. Allow extra room between the plants, and avoid overhead watering, especially late in the day. Purchase certified disease-free seeds and plants. Destroy volunteer tomato and potato plants and nightshade family weeds, which may harbor the fungus. Do not compost rotten, store-bought potatoes. Pull out and destroy diseased plants. If disease is severe enough to warrant chemical control, select one of the following fungicides: chlorothalonil (very good); copper fungicide, or mancozeb (good). See Table 1 for examples of fungicide products for home garden use. Follow the directions on the label. Plant resistant cultivars. See Table 3 for tomato cultivars with resistance to late blight"

        elif preds==3:
            preds="Tomato__Leaf_Mold"
            a = "Prevention and treatment"
            content = "Crop residue should be removed from the field. Staking and pruning to increase air circulation helps to control the disease. Avoid wetting leaves when watering. Rotate with vegetables other than tomatoes. Using a preventative fungicide program with chlorothalonil, mancozeb or copper fungicide, can control the disease"

        elif preds==4:
            preds="Tomato__Septoria_leaf_spot"
            a = "Prevention and treatment"
            content = "Currently grown tomato cultivars are susceptible to Septoria leaf spot. Crop rotation of 3 years and sanitation (removal of crop debris) will reduce the amount of inoculum. Do not use over-head irrigation. Repeated fungicide applications with chlorothalonil (very good) or copper fungicide, or mancozeb (good) will keep the disease in check."

        elif preds==5:
            preds="Tomato__Spider_mites Two-spotted_spider_mite"
            a = "Prevention and treatment"
            content = "Since mite development is linked to host plant stress, cultural practices and varieties that limit plant stress in times of drought will also minimize the development of spider mites. Spider mite activity may be adversely affected by the onset of rains depending on the level of mite infestation established. Rains may have a negative effect on a minor infestation. However, well-established mite populations may tolerate significant rains, especially if host plants are already in a condition of stress."

        elif preds==6:
            preds="Tomato___Target_Spot"
            a = "Prevention and treatment"
            content = "This fungal disease can last up to 2 years in leftover plant debris from your garden. So appropriate cleaning out of your garden every year will be a good preventive measure to keep this disease off your plants and fruit. The leaves will have small back dots when target spot is beginning. Spraying with a fungicide periodically is the only other known preventive measure to keep your tomatoes from the target spot disease."

        elif preds==7:
            preds="Tomato___Tomato_Yellow_Leaf_Curl_Virus"
            a = "Prevention and treatment"
            content = "Removal of plants with initial symptoms may slow the spread of the disease. Rogued (pulled out) infected plants should be immediately bagged to prevent the spread of the whiteflies feeding on those plants. Keep weeds controlled within and around the garden site, as these may be alternate hosts for whiteflies. Reflective mulches (aluminum or silver-colored) can be used in the rows to reduce whitefly feeding."
    
        elif preds==8:
            preds="Tomato___Tomato_mosaic_virus"
            a = "Prevention and treatment"
            content = "There are numerous tomato varieties that are resistant to one or the other of the viruses. These are usually denoted in seed catalogs, often with the code ToMV after the variety name if resistant to tomato mosaic virus and TMV if resistant to tobacco mosaic virus. There are only a few varieties that are resistant to both viruses. Several popular rootstocks for grafted tomatoes can also confer resistance to varieties that may not normally be resistant."

        else:
            preds="Tomato___healthy"
        
        return render(request, "farmer/cropdisease.html",{'preds':preds ,'a': a, 'uploaded_file_url': uploaded_file_url, 'content':content})
    return render(request , "farmer/cropdisease.html")


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

