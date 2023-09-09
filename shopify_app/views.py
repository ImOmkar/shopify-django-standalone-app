import os
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import requests
import shopify
import json
from dotenv import load_dotenv

load_dotenv()


# Create your views here.


SOCIAL_AUTH_SHOPIFY_KEY   = os.getenv('SOCIAL_AUTH_SHOPIFY_KEY')
SOCIAL_AUTH_SHOPIFY_SECRET = os.getenv('SOCIAL_AUTH_SHOPIFY_SECRET')
SHOP_NAME = os.getenv('SHOP_NAME')
SOCIAL_AUTH_SHOPIFY_SCOPE = os.getenv('SOCIAL_AUTH_SHOPIFY_SCOPE')
SOCIAL_AUTH_SHOPIFY_API_VERSION = os.getenv('SOCIAL_AUTH_SHOPIFY_API_VERSION')
REDIRECT_URI = os.getenv('REDIRECT_URI')


@csrf_protect
def login(request):
    if request.method == 'POST':
        shop = request.POST.get('shop')
        auth_url = "{}/admin/oauth/authorize?client_id={}&scope={}&redirect_uri={}".format(shop, SOCIAL_AUTH_SHOPIFY_KEY, SOCIAL_AUTH_SHOPIFY_SCOPE, REDIRECT_URI)
        print(auth_url)
        return redirect(auth_url)
    return render(request, 'home.html')


def connect(request):
    if request.GET.get('shop'):
        params = {
            'client_id': SOCIAL_AUTH_SHOPIFY_KEY,
            'client_secret': SOCIAL_AUTH_SHOPIFY_SECRET,
            'code': request.GET.get('code')
        }
        response = requests.post(
            "https://{}/admin/oauth/access_token".format(request.GET.get('shop')),
            data = params
        )

    if 200 == response.status_code:
        response_json = json.loads(response.text)

        request.session['access_token'] = response_json.get('access_token')
        request.session['shop'] = request.GET.get("shop")

        return redirect('welcome')



def webhooks(request):
    token = request.session['access_token']
    shop = request.session['shop']
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    endpoint = f"https://{shop}/admin/api/{SOCIAL_AUTH_SHOPIFY_API_VERSION}/webhooks.json"

    response = requests.get(endpoint, headers=headers)

    webhooks = json.loads(response.text)

    return render(request, 'webhooks.html', context={'webhooks': webhooks.get("webhooks"), "token": token, "shop": shop})


def register_to_webhook(request):

    token = request.session['access_token']
    shop = request.session['shop']

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    if request.method == 'POST':
        topic = request.POST.get('topic')
        address = request.POST.get('address')
        print(topic, address)
        
        payload = {
            "webhook": {
                "topic": topic,
                "address": address,
                "format": "json"
            }
        }

        data = json.dumps(payload)
        endpoint = f"https://{shop}/admin/api/{SOCIAL_AUTH_SHOPIFY_API_VERSION}/webhooks.json"
        print(endpoint)
        try:
            response = requests.post(endpoint, data=data, headers=headers)
        except Exception as e:
            print(e)
        webhooks = json.loads(response.text)
        messages.success(request, 'Registered to a Webhook')
        return redirect('webhooks')



def delete_webhook(request, id):
    token = request.session['access_token']
    shop = request.session['shop']
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }
    endpoint = f"https://{shop}/admin/api/{SOCIAL_AUTH_SHOPIFY_API_VERSION}/webhooks/{id}.json"
    response = requests.delete(endpoint, headers=headers)
    messages.success(request, 'Webhook removed')
    return redirect('webhooks')



def welcome(request):
    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)

    shop_name = shopify.Shop.current
    

    return render(request, 'welcome.html', locals())


def product_list(request):

    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)
    products = shopify.Product.find()
    context = {
        'products': products
    }
    return render(request, 'product_list.html', context)



def details(request, id):
    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)

    product = shopify.Product.find(id)
    return render(request, "details.html", locals())



def create_product(request):
    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)
    new_product = shopify.Product()
    if request.method == 'POST':
        new_product.title = request.POST.get('title')
        new_product.product_type = request.POST.get('type')
        new_product.image = request.POST.get('image')
        new_product.vendor = request.POST.get('vendor')
        new_product.save()
        messages.success(request, 'Product created')
        return redirect('product_list')
    return render(request, "create_product.html", locals())


def update(request, id):
    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)
    product = shopify.Product.find(id)
    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.product_type = request.POST.get('type')
        product.vendor = request.POST.get('vendor')
        product.save()
        messages.success(request, 'Product updated')
        return redirect('product_list')
    return render(request, "update.html", locals())

def delete(request, id):
    token = request.session['access_token']
    shop = request.session['shop']
    shop_url = f"https://{shop}.myshopify.com"
    session = shopify.Session(shop_url, SOCIAL_AUTH_SHOPIFY_API_VERSION, token)
    shopify.ShopifyResource.activate_session(session)

    shopify.Product.delete(id)
    messages.success(request, 'Product removed')
    return redirect('product_list')
    #return render(request, "my_app/details.html", locals())




#fetch, update, write, delete using API endpoints

def product_list_endpoint(request):
    token = request.session['access_token']
    shop = request.session['shop']
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    endpoint = f"https://{shop}/admin/api/{SOCIAL_AUTH_SHOPIFY_API_VERSION}/products.json"
    
    response = requests.get(endpoint, headers=headers)

    
    products = json.loads(response.text)


    return render(request, 'endpoint_product_list.html', context={'products': products.get("products")})

def single_product_endpoint(request, id):
    token = request.session['access_token']
    shop = request.session['shop']
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    endpoint = f"https://{shop}/admin/api/{SOCIAL_AUTH_SHOPIFY_API_VERSION}/products/{id}.json"
    
    response = requests.get(endpoint, headers=headers)

    
    products = json.loads(response.text)
   

    return render(request, 'single_product_endpoint.html', context={'products': products.get("products")})












