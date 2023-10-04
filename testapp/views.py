from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
from django.shortcuts import redirect
import json
from django.contrib.auth import login, authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def is_admin(response):
    if not response.user.is_authenticated:
        return False
    if not  response.user.is_admin():
        return False

    return True

def admin_required(view):
    def wrapper(response):
        if is_admin(response):
            return view(response)
        return redirect(promoted_page)
    return wrapper

def get_distinct_categories():
    categories_ids = Product.objects.values("category").distinct()
    categories = []
    for cat_id in categories_ids:
        categories.append(Product_category.objects.get(id=cat_id['category']))
    return categories

def get_promoted_categories():
    categories_ids = Product.objects.filter(promoted=True).values("category").distinct()
    categories = []
    for cat_id in categories_ids:
        categories.append(Product_category.objects.get(id=cat_id['category']))
    return categories


def get_basepage_data(response):
    return {"categories":get_distinct_categories(),"user":response.user}


def basket_page(response):
    return render(response,'basket.html',get_basepage_data(response))

def not_found(response):
    return render(response,'no_page.html',get_basepage_data(response))

def contact_form(response):
    if response.method=="POST":
        if response.POST.get('contact-form-submit'):
            contact_form_name = response.POST.get('contact-form-name')
            contact_form_email = response.POST.get('contact-form-email')
            contact_form_content = response.POST.get('contact-form-content')
            send_mail(
                subject="Dziękujemy za kontakt z Pieczarki.pl",
                message="Dziękujemy za kontakt ze sklepem Pieczarki.pl. Pańskie zgłoszenie zostało przyjęte, wkrótce skontaktuje się z tobą nasz konsultant.",
                from_email='email',
                recipient_list=[contact_form_email],
                auth_user='user',
                auth_password="passwd",
            )
            return redirect(contact_complete)

    page_data = get_basepage_data(response) 
    return render(response,'contact_page.html',page_data)

def contact_complete(response):
    return render(response,'contact_complete.html',get_basepage_data(response))

def register_user(response):
    
    register_error = ""

    if response.method == "POST":
        if response.POST.get("register_submit"):
            username = response.POST.get('username')
            email = response.POST.get('email')
            passwd1 = response.POST.get('passwd1')
            passwd2 = response.POST.get('passwd2')
            is_admin = True if response.POST.get('is_admin') else False

            is_password_valid = True
    
            if passwd1 != passwd2:
                is_password_valid = False
                register_error += "<li>Podane hasła nie są takie same</li>"
            if len(passwd1) < 8 or len(passwd2) < 8:
                is_password_valid = False
                register_error += '<li>Hasło musi zawierac conajmniej 8 znakówi</li>'

            if is_password_valid:
                user = CustomUser.objects.create_user(username=username,email=email,password=passwd1,user_type=(1 if is_admin == True else 0))
                user.save()
                register_error = ""
                login(response,user)
                return redirect(promoted_page)

    data = get_basepage_data(response)
    data['register_error'] = register_error
    return render(response,'register_page.html',data)


def login_user(response):
    if not response.user.is_authenticated:
        login_error = ""
        if response.method == "POST":
            if response.POST.get("login_btn"):
                username = response.POST['username']
                password = response.POST['passwd']
                user = authenticate(request = response,username=username,password=password)
                if user is not None:
                    login(response,user)
                    return redirect(promoted_page)
                else:
                    login_error = 'Nieprawidłowe dane logowania!'
        
        data = get_basepage_data(response)
        data['login_error'] = login_error
        return render(response,'login_page.html',data)
    return redirect(promoted_page)

def logout_user_view(response):
    logout(response)
    return redirect(login_user)

@login_required
def user_page(response):
    data = get_basepage_data(response)
    data['purchases'] = Purchase.objects.filter(user=response.user)
    return render(response,'user_page.html',data)


def place_order(response):
    if response.method == 'POST':
        if response.POST.get("products_list"):

            products = json.loads(response.POST.get('products_list'))

            if len(products)>0:

                email = None
                user = response.user

                if response.user.is_anonymous:
                    user = None
                    email = response.POST.get('anon_user_email')
                    if not email:
                        print("email is none")
                        print(email)
                        return HttpResponse("W przypadku składania zamówienia jako niezlogowany użytkownik wymagane jest podanie adresu email")
                else:
                    email = user.email
                
                new_purchase = Purchase(user=user,email=email)
                products_objects = Product.objects.all()

                orders_batch = (Purchase_item(purchase = new_purchase,amount=products[product],product=products_objects.get(id=product)) for product in products)
        
                if orders_batch:
                    new_purchase.save()
                    Purchase_item.objects.bulk_create(orders_batch)

            
    return HttpResponse("OK")

def order_complete(response):
    return render(response,"order_complete.html",get_basepage_data(response))

@admin_required
@login_required
def show_all_purchases(response):
    page_data = get_basepage_data(response)
    page_data['purchases'] = Purchase.objects.all()
    return render(response,'purchases_view.html',page_data)

def order_finalization(response):
    page_data = get_basepage_data(response) 
    return render(response,'order_final_page.html',page_data)

@admin_required
@login_required
def magazine_panel(response,magazine_id):
    page_data=get_basepage_data(response)
    page_data["magazine"]   = Magazine.objects.get(id=magazine_id)
    return render(response,'magazine_panel.html',page_data)

@admin_required
@login_required
def add_stock(response,magazine_id):
    magazine = Magazine.objects.get(id=magazine_id)
    if response.method == "POST":
        if response.POST.get("add_btn"):
            product = Product.objects.get(id=response.POST.get("product_id"))
            stock = None
            try:
                stock = Product_stock.objects.get(magazine=magazine,product=product)
            except:
                stock = Product_stock(magazine=magazine,product=product)
                
            stock.stock = stock.stock+int(response.POST.get("add_stock_amount"))
            stock.save()

            return redirect(f'/magazine/{str(magazine_id)}')


    page_data = get_basepage_data(response)
    page_data["magazine"]   = magazine
    page_data["products"]   = Product.objects.all()
    return render(response,'add_stock.html',page_data)

@admin_required
@login_required
def magazines_list(response):
   
    if response.method == "POST":
        if response.POST.get("add_magazine_btn"):
            magazine = Magazine(magazine_name=response.POST.get("add_magazine_name")) 
            magazine.save()

    page_data = get_basepage_data(response)
    page_data["magazines"] = Magazine.objects.all()
    return render(response,"magazines.html",page_data)

@admin_required
@login_required
def del_stock(response,magazine_id):
    magazine = Magazine.objects.get(id=magazine_id)
    if response.method == "POST":
        if response.POST.get("del_btn"):
            product = Product.objects.get(id=response.POST.get("product_id"))
            try:
                stock = Product_stock.objects.get(magazine=magazine,product=product)
                stock.stock = stock.stock-int(response.POST.get("add_stock_amount"))
                stock.save()
                if stock.stock <= 0:
                    stock.delete()
            except:
                pass
            return redirect(f'/magazine/{str(magazine_id)}')


    page_data = get_basepage_data(response)
    page_data["magazine"]   = magazine
    page_data["products"]   = Product.objects.all()
    return render(response,'del_stock.html',page_data)

def categories_list_full(response):
    categories = []
    for category in Product_category.objects.all():
        categories.append({"id":category.id,"name":category.category_name})
    return JsonResponse(categories,safe=False)

def categories_list_no_empty(response):
    categories = []
    for category in get_distinct_categories():
        categories.append({"id":category.id,"name":category.category_name})

    return JsonResponse(categories,safe=False)

def categories_list_promoted(response):
    categories = []
    for category in get_promoted_categories():
        categories.append({"id":category.id,"name":category.category_name})
    return JsonResponse(categories,safe=False)

@admin_required
@login_required
def add_category_page(response):
   
    if response.method == "POST":
        category = Product_category(category_name  = response.POST.get("category_name"))
        category.save()
        return redirect('/')
    
    page_data = get_basepage_data(response)
    return render(response,'add_category.html',page_data)

def get_promoted_products_list():
    return Product.objects.filter(promoted=True)

def get_promoted_products_list(response,category_id=0):
    products_data = []
    products = []

    if category_id == 0:
        products = Product.objects.filter(promoted=True)
    else:
        products = Product.objects.filter(category = Product_category.objects.get(id=category_id),promoted=True)
    for product in products:
        products_data.append({
            "id":product.id,
            "name":product.product_name,
            "description":product.description,
            "promoted":product.promoted,
            "brutto_price":product.get_brutto_price(),
            "netto_price":product.get_netto_price(),
            "tax_value":product.tax.tax_value,
            "stock":product.get_total_stock()
        })

    return JsonResponse(products_data,safe=False)

def promoted_page(response):
    page_data = get_basepage_data(response)
    return render(response,"promoted.html",page_data)

def get_products_data(response,product_id = 0):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse(product.as_table(),safe=False)
    
    except:
        return JsonResponse({"name":"none"},safe=False)

def get_products_list_from_json(response):
    if response.method == "POST":
        objects_list = json.loads(response.POST['objects_list'])
        #print(objects_list)
        product_list = []
        for product_index in objects_list:
            product_list.append(Product.objects.get(id=product_index).as_table())
    
        return JsonResponse(product_list,safe=False)
    return HttpResponse("No object list provided!")

def get_products_list(response,category_id = 0):
    products_data = []
    products = []

    if category_id == 0:
        products = Product.objects.all().order_by("-promoted")
    else:
        products = Product.objects.filter(category = Product_category.objects.get(id=category_id)).order_by("-promoted")
    for product in products:
        products_data.append(product.as_table())

    return JsonResponse(products_data,safe=False)

def product_page(response,product_id):
    page_data = get_basepage_data(response)
    page_data['product'] = Product.objects.get(id=product_id)
    return render(response,'product_page.html',page_data)

def show_products(response,category_id=0):
    page_data = get_basepage_data(response)
    if category_id == 0:
        return render(response,"all_products.html",page_data)
    else:
        page_data["category"] = Product_category.objects.get(id=category_id)
        return render(response,"all_products_from_category.html",page_data)

@admin_required
@login_required
def add_product_page(response):
    
    if response.method == "POST":
        price = int(float(str(response.POST.get("price")).replace(',','.'))*100.0)

        prod = Product(
            product_name    = response.POST.get("product_name"),
            price           = price,
            promoted        = True if response.POST.get("promoted") != None else False,
            description     = response.POST.get("description"),
            category        = Product_category.objects.get(id=response.POST.get("category")),
            tax             = Tax.objects.get(id=response.POST.get("tax")))
        prod.save()
        return redirect('/')

    page_data = get_basepage_data(response)
    page_data["taxes"] = Tax.objects.all()
    page_data["all_categories"] = Product_category.objects.all()

    return render(response,'add_product.html',page_data)

@admin_required
@login_required
def edit_product_page(response, product_id):
    product = Product.objects.get(id=product_id)

    if response.method == "POST":
        if response.POST.get("add_btn"):
            price = int(float(str(response.POST.get("price")).replace(',','.'))*100.0)
            product.product_name    = response.POST.get("product_name")
            product.price           = price
            product.promoted        = True if response.POST.get("promoted") != None else False
            product.description     = response.POST.get("description")
            product.category        = Product_category.objects.get(id=response.POST.get("category"))
            product.tax             = Tax.objects.get(id=response.POST.get("tax"))
            product.save()
        elif response.POST.get("del_btn"):
            product.delete()

        return redirect('/')

    page_data = get_basepage_data(response)
    page_data['product'] = product
    page_data['all_categories'] = Product_category.objects.all()
    page_data["taxes"] = Tax.objects.all()
    return render(response,'edit_product.html',page_data)
