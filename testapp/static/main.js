function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

function generate_product_list_item_html(item){
    product = '';
    if(item.promoted == false){
        product += '<div class="container m-2 p-2 rounded-2 border">'
    }else{
        product += '<div class="container m-2 p-2 rounded-2 border border-warning">'
    }
    product += '<div class="row align-items-center d-flex justify-content-center">'
    product += '<a href="/product/'+item.id+'" class="col-2 btn">'+item.name+'</a>'
    product += '<div class="col">'+item.description+'</div>'
    product += '<div class="col-1">'+item.brutto_price+' zł/kg</div>'
    if(item.stock > 0){
        product += '<div class="col-2 d-flex justify-content-center btn btn-primary" onClick="add_to_basket('+item.id+',1)">Dodaj do koszyka</div>'
    }else{
        product += '<div class="col-2 d-flex justify-content-center btn btn-secondary disabled">Produkt niedostępny</div>'
    }
    product += '</div></div>'
    return product;
}

function place_order(){
    let basket = get_basket();

    //console.log("email: "+$('#anon_user_email').val())
    
    if(!$.isEmptyObject(basket)){
        $.ajax({
            url:"/place_order",
            type:"POST",
            data:{'products_list':JSON.stringify(basket),
                    'anon_user_email':$('#anon_user_email').val()},
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken',getCookie('csrftoken'))
            }
        }).done(function(data){
            if (data == 'OK'){
                clear_basket();
                window.location.replace('/order_complete')
            }else{
                $('#basket_error').html(data)
            }

        })
    }
}

function generate_final_order_list(element,api_url = '/get_products_list_from_json'){
    $(element).html("")
    basket = get_basket()
    if(!$.isEmptyObject(basket)){
        $.ajax({
            url:api_url,
            type:"POST",
            data:{'objects_list':JSON.stringify(basket)},
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken',getCookie('csrftoken'))
            }
        }).done(function(json_data){
            final_order_price = Number(0);
            $.each(json_data,function(key,item){
                amount = basket[item.id]
                final_order_price+=Number((amount*item.brutto_price).toFixed(2));
                order_item = ""
                order_item += '<div class="container m-2 p-2 rounded-2 border">'
                order_item += '<div class="row align-items-center d-flex justify-content-center">'
                order_item += '<div class="col-4">Produkt: '+item.name+'</div>'
                order_item += '<div class="col-2">Ilość: '+amount+'kg</div>'
                order_item += '<div class="col d-flex justify-content-end">Cena: '+(amount*item.brutto_price).toFixed(2)+'zł Brutto</div>'
                order_item += '</div></div>'
                $(element).append(order_item)   
            })
            $(element).append('<div class="row d-flex justify-content-end">Razem do zapłaty: '+final_order_price+'zł</div>')
        })
    }
}

function add_category(category_name,category_select_element){
    $.ajax({
        url:"/category/add",
        type:"POST",
        data:{'category_name':$(category_name).val()},
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken',getCookie('csrftoken'))
        }
    }).done(function(data){
        console.log('DONE!')
        $(category_select_element).html("")
        update_categories_select(category_select_element,'/category/get_categories_list_full')
    })
}

function update_basket(element,api_url = '/get_products_list_from_json'){
    $(element).html("")
    basket = get_basket()
    if(!$.isEmptyObject(basket)){
        $.ajax({
            url:api_url,
            type:"POST",
            data:{'objects_list':JSON.stringify(basket)},
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken',getCookie('csrftoken'))
            }
        }).done(function(json_data){
            $.each(json_data,function(key,value){
                amount = basket[value.id]
                basket_item = ""
                basket_item += '<div class="container m-2 p-2 rounded-2 border">'
                basket_item += '<div class="row align-items-center d-flex justify-content-center">'
                basket_item += '<div class="col-4">Produkt: '+value.name+'</div>'
                basket_item += '<div class="col-2">Ilość: '+amount+'kg</div>'
                basket_item += '<div class="col d-flex justify-content-end">Cena: '+(amount*value.brutto_price).toFixed(2)+'zł Brutto</div>'
                basket_item += '<div class="fs-3 btn col-1 d-flex justify-content-center" onClick="remove_from_basket('+value.id+',1);update_basket(\''+element+'\')">-</div>'
                basket_item += '<div class="fs-3 btn col-1 d-flex justify-content-center" onClick="add_to_basket('+value.id+',1);update_basket(\''+element+'\')">+</div>'
                basket_item += '</div></div>'
                $(element).append(basket_item)
            })
            $(element).append('<div class="row d-flex justify-content-end">')
            $(element).append('<div class=" col d-flex justify-content-start "><a class="fs-3 btn" href="/order_finalization">Przejdź do płatności</a></div>')
            $(element).append('<div class=" col d-flex justify-content-end"><div class="btn" onClick="clear_basket();update_basket(\'#basket\');">Wyczyść koszyk</div></div>')
            $(element).append('</div>')
            
        })
    }
    else{
        $(element).html('<div class="fs-1 m-3">Koszyk jest pusty</div><a href="/products/all" class="btn">Wróć na stronę z produktami</a>')
    }
    
}

function update_product_list(element,api_url,id=0){
    
    if(api_url[api_url.length-1] !='/') api_url+='/'

    $.ajax({url:api_url+id}).done(function(products){

        $(element).html("")
        
        $.each(products,function(index,item){
            product = generate_product_list_item_html(item)
            $(element).append(product)
        });

    })
}

function update_categories_menu(element,api_url){
    $.ajax({url:api_url}).done(function(categories){
        $.each(categories,function(index,item){
            $(element).append('<a class="col btn d-flex justify-content-start" href="/products/'+item.id+'">'+item.name+'</a>')
        })
    })
}

function update_categories_select(element,api_url){
    $.ajax({url:api_url}).done(function(categories){
        $.each(categories,function(index,item){
            $(element).append('<option value="'+item.id+'">'+item.name+'</option>')
        })
    })
}

function get_basket(){
    basket = jQuery.parseJSON(localStorage.getItem("basket"))
    
    if(basket == null){
        basket = {}
    }

    return basket;
}

function get_basket_size(){
    basket = get_basket()

    amount = 0;
    $.each(basket,(index,item)=>{
        amount += item
    })

    return amount
}

function add_to_basket(product_id,amount){
    basket = jQuery.parseJSON(localStorage.getItem("basket"))
    if(basket == null){
        basket = {}
    }
    
    if(basket[product_id] == null){
        basket[product_id] = 0;
    }

    basket[product_id] += amount
    localStorage.setItem("basket",JSON.stringify(basket))
}

function remove_from_basket(product_id,amount){
    basket = jQuery.parseJSON(localStorage.getItem("basket"))
    
    if(basket[product_id] == null){
        basket[product_id] = 0;
    }
    
    basket[product_id] -=amount
    if(basket[product_id] <=0){
        delete basket[product_id]
    }
    localStorage.setItem("basket",JSON.stringify(basket))
}

function clear_basket(){
    localStorage.removeItem("basket",{})
}
