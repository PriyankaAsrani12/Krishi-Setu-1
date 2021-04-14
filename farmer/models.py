from django.db import models

# Create your models here.
class AddProduct(models.Model):
    product_id=models.AutoField
    category=models.CharField(max_length=50)
    sub_category=models.CharField(max_length=50)
    variety=models.CharField(max_length=50)
    aln=models.CharField(max_length=50)
    location=models.CharField(max_length=1000)
    quantity=models.IntegerField()
    price=models.IntegerField()
    pub_date=models.DateField()
    image=models.FileField(upload_to='', null=True, verbose_name="")

    def __str__(self):
        return self.sub_category


