from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("",views.index,name="FarmerHome"),
    path("about",views.about,name="About"),
    path("news",views.news,name="News"),
    path("fullnews",views.fullnews,name="FullNews"),
    path("tutorials",views.tutorials,name="Tutorials"),
    path("cropinfo",views.cropinfo,name="Cropinfo"),
    path("contact",views.contact,name="Contact"),
    path("dashboard",views.dashboard,name="Dashboard"),
    path("login",views.handlelogin,name="Login"),
    path("logout",views.handlelogout,name="Logout"),
    path("signup",views.signup,name="SignUp"),
    path("cropdisease",views.cropdisease,name="CropDisease"),
    path("addproduct",views.addproduct,name="AddProduct"),
    path("StatewiseProductPrice",views.StatewiseProductPrice,name="StatewiseProductPrice"),
    path("cropDiseasePrediction",views.cropDiseasePrediction,name="cropDiseasePrediction"),
]