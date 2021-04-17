from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="ShopHome"),
    path('about',views.about,name="About"),
    path('news',views.news,name="News"),
    path('contact',views.contact,name="Contact"),
    path('tracker',views.tracker,name="Tracker"),
    path('products/<str:myid>',views.productview,name="ProductView"),
    path('search',views.search,name="Search"),
    path('checkout',views.checkout,name="Checkout"),
    path("login",views.handlelogin,name="Login"),
    path("logout",views.handlelogout,name="Logout"),
    path('signup',views.signup,name="SignUp"),
    path('charge',views.charge,name="Charge"),
    path('payment', views.HomePageView.as_view(), name='home'),
    path('history', views.history, name='History'),
    path('orderdetail/<str:myid>', views.orderdetail, name='OrderDetail'),
    path('rating/<int:myid>', views.rating, name='Rating')
]