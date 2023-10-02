from django.urls import path, re_path
from . import views
from django.urls import include

urlpatterns = [
    path('',views.promoted_page),

    path('get_products_list',views.get_products_list),
    path('get_products_list/<int:category_id>',views.get_products_list),

    path('get_product/<int:product_id>',views.get_products_data),
    path('get_products_list_from_json',views.get_products_list_from_json),

    
    path('get_promoted_products_list',views.get_promoted_products_list),
    path('get_promoted_products_list/<int:category_id>',views.get_promoted_products_list),

    path('products/all',views.show_products),
    path('products/<int:category_id>',views.show_products),

    path('product/<int:product_id>',views.product_page),
    path('product/add',views.add_product_page),
    path('product/edit/<int:product_id>',views.edit_product_page),

    
    path('category/add',views.add_category_page),
    path('category/get_categories_list_full',views.categories_list_full),
    path('category/get_categories_list_no_empty',views.categories_list_no_empty),
    path('category/get_categories_list_promoted',views.categories_list_promoted),

    path('basket',views.basket_page),

    path('place_order',views.place_order),
    path('order_finalization',views.order_finalization),
    path('order_complete',views.order_complete),
    path('all_orders',views.show_all_purchases),

    path('magazines',views.magazines_list),
    path('magazine/<int:magazine_id>',views.magazine_panel),
    path('magazine/add_stock/<int:magazine_id>',views.add_stock),
    path('magazine/del_stock/<int:magazine_id>',views.del_stock),

    path('user',views.user_page),
    path('user/register',views.register_user),
    path('user/login',views.login_user),
    path('user/logout',views.logout_user_view),

    path('contact',views.contact_form),
    path('contact_complete',views.contact_complete),

    re_path('.*',views.not_found),

]