from django.db import models
from django.db.models import Sum
from math import ceil
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    user_type = models.IntegerField(default=0) #0 = user, 1=admin

    def is_admin(self):
        return True if self.user_type == 1 else False

class Product_category(models.Model):
    category_name = models.CharField(max_length=32)
    def __str__(self):
        return str(self.category_name)

class Tax(models.Model):
    tax_value = models.IntegerField(default=23)
    def __str__(self):
        return str(self.tax_value/100.0)

class Magazine(models.Model):
    magazine_name = models.CharField(max_length=32)

    def get_stocks(self):
        product_ids = Product_stock.objects.filter(magazine=self).values('product').distinct()
        stocks = []
        for prod_id in product_ids:
            product = Product.objects.get(id=prod_id["product"])
            stock = [product,Product_stock.objects.filter(product=product,magazine = self).aggregate(Sum('stock'))['stock__sum']]
            stocks.append(stock)
        return stocks

    def __str__(self):
        return str(self.magazine_name)

class Product(models.Model):
    product_name    = models.CharField(max_length=32)
    price           = models.IntegerField(default = 0)
    promoted        = models.BooleanField(default = False)
    category        = models.ForeignKey(Product_category,on_delete = models.PROTECT,null=True)
    tax             = models.ForeignKey(Tax,on_delete = models.PROTECT,null=True)
    description     = models.CharField(max_length=400,null=True)

    def get_netto_price(self):
        return self.price / 100.0

    def get_brutto_price(self):
        return ceil(self.price*(1+self.tax.tax_value/100.0))/100.0

    def __str__(self):
        return str(self.product_name)

    def get_stock(self):
        magazine_ids = Product_stock.objects.values('magazine').distinct()
        stocks = []
        for mag_id in magazine_ids:
            magazine = Magazine.objects.get(id=mag_id["magazine"])
            stock = [magazine,Product_stock.objects.filter(product=self,magazine = mag_id["magazine"]).aggregate(Sum('stock'))['stock__sum']]
            stocks.append(stock)
        #print(stocks)
        return stocks
    def get_total_stock(self):
        stocks = self.get_stock()
        total = 0
        for stock in stocks:
            try:
                total = total+stock[1]
            except:
                pass
        return total
    def as_table(self):
        return {
            "id":self.id,
            "name":self.product_name,
            "description":self.description,
            "promoted":self.promoted,
            "brutto_price":self.get_brutto_price(),
            "netto_price":self.get_netto_price(),
            "tax_value":self.tax.tax_value,
            "stock":self.get_total_stock()
        }

class Product_stock(models.Model):
    magazine    = models.ForeignKey(Magazine,on_delete=models.CASCADE)
    product     = models.ForeignKey(Product,on_delete=models.CASCADE)
    stock       = models.IntegerField(default=0)


class Purchase(models.Model):
    purchase_date = models.DateTimeField()
    user = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,null=True)
    email = models.EmailField(null=True)


    def get_ordered_products(self):
        return Pruchase_item.objects.filter(purchase=self)

class Pruchase_item(models.Model):
    purchase    = models.ForeignKey(Purchase,on_delete = models.DO_NOTHING)
    product     = models.ForeignKey(Product,on_delete = models.DO_NOTHING)
    amount      = models.IntegerField()
    def get_brutto_price(self):
        return self.amount*self.product.get_brutto_price()
    def get_netto_price(self):
        return self.amount * self.product.get_netto_price()