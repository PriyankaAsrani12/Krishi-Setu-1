from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import AddProduct
admin.site.register(AddProduct)
admin.site.register(Permission)