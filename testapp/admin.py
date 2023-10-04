from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

admin.site.register(Product_category)
admin.site.register(Tax)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Purchase_item)
admin.site.register(Magazine)
admin.site.register(Product_stock)
admin.site.register(CustomUser,UserAdmin)

# Register your models here.
