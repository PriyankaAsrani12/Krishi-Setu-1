from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages

# Create your views here.
def index(request):
    logout(request)
    return render(request,"index (2).html")
