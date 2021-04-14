from django.db import models

# Create your models here.
class Product(models.Model):
    product_id=models.AutoField
    category=models.CharField(max_length=50)
    sub_category=models.CharField(max_length=50)
    variety=models.CharField(max_length=50)
    location=models.CharField(max_length=1000)
    quantity=models.IntegerField()
    price=models.IntegerField()
    pub_date=models.DateField()
    image=models.FileField(upload_to='shop/images/', null=True, verbose_name="")

    def __str__(self):
        return self.sub_category

class Contact(models.Model):
    msg_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=70)
    email=models.CharField(max_length=100,default="")
    subject = models.CharField(max_length=50,default="")
    phone=models.CharField(max_length=50,default="")
    desc=models.CharField(max_length=10000,default="")

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    name=models.CharField(max_length=70)
    amount=models.IntegerField(default=0)
    email = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=50, default="")
    address = models.CharField(max_length=5000, default="")
    city = models.CharField(max_length=100,default="")
    state = models.CharField(max_length=100,default="")
    zip_code = models.CharField(max_length=50,default="")

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc=models.CharField(max_length=5000)
    timestamp=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.update_desc[0:17]+"..."
