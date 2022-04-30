from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
#from .forms import userRegistrationForm
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage

######  email ########
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import date


def store(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        itemsCount = 0
        for item in items:
            itemsCount += item.quantity

    else:
        itemsCount = 0

    categories = Category.objects.all()
    products = Product.objects.all()

    p = request.GET.get("p")
    if p == "high":
        products = Product.objects.order_by("-price")
    else:
        products = Product.objects.order_by("price")

    q = request.GET.get("q")
    if q != None:
        products = Product.objects.filter(
            Q(category__name__icontains=q) |
            Q(name__icontains=q)
        )

    
    # num of pages
    p = Paginator(products, 5)
    # print(p.num_pages)
    page_num = request.GET.get("page", 1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    numberOfPagesPaggination = p.num_pages

    context = {"products": page, "itemsCount": itemsCount, "categories": categories,
               "numberOfPagesPaggination": numberOfPagesPaggination}
    return render(request, "store/store.html", context)


@login_required(login_url="/accounts/login")
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        itemsCount = 0
        totalOrderPrice = 0
        for item in items:
            itemsCount += item.quantity
            totalOrderPrice += item.totalPrice

    else:
        items = []
        itemsCount = 0
        totalOrderPrice = 0

    context = {"items": items, "itemsCount": itemsCount, "totalOrderPrice": totalOrderPrice}
    return render(request, "store/cart.html", context)


@login_required(login_url="/accounts/login")
def checkout(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()

    totalOrderPrice = 0
    itemsCount = items.count()

    for item in items:
        totalOrderPrice += item.totalPrice

    if request.method == "POST":
        address = request.POST.get("address")
        city = request.POST.get("city")
        phone = request.POST.get("phone")

        if len(phone) < 11:
            messages.error(request, 'Phone number should be 11 numbers')
            return redirect('/checkout')

        shipping_date, created = ShippingAddress.objects.get_or_create(
            customer=customer,
            order=order,
            address=address,
            city=city,
            phone=phone,
        )

        itemsCount = items.count()
        totalOrderPrice = 0
        for item in items:
            totalOrderPrice += item.totalPrice

        content = {"items": items, "order": order, "itemsCount": itemsCount,"totalOrderPrice": totalOrderPrice,"phone":phone,"city":city,"address":address}

        html_content = render_to_string("store/email_template.html", content)
        text_content = strip_tags(html_content)
        to = customer.email

        email = EmailMultiAlternatives(
            # subject
            "New order",
            # content
            text_content,
            # from email
            settings.EMAIL_HOST_USER,
            # recivers list
            [to]
        )
        email.attach_alternative(html_content, "text/html")

        email.send()

        messages.success(request, 'Order completed')
        

        order.delete()
        items = ""
        itemsCount = 0
        totalOrderPrice = 0


    context = {"items": items, "itemsCount": itemsCount, "totalOrderPrice": totalOrderPrice}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    product_id = data["product_id"]
    action = data["action"]

    customer = request.user
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)

#
# def loginPage(request):
#     if request.user.is_authenticated:
#         return redirect("/")
#
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         try:
#             user = User.objects.get(username=username)
#         except:
#             messages.error(request, 'User Not found')
#
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, 'Login successful')
#             return redirect("/")
#         else:
#             messages.error(request, 'User or password not found')
#
#     return render(request, "registration/login.html")
#
#
# def registerPage(request):
#     form = userRegistrationForm()
#     if request.method == "POST":
#         form = userRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data["username"]
#             password = form.cleaned_data["password1"]
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             messages.success(request, 'Registration Successful!')
#             return redirect("/")
#         else:
#             messages.error(request, 'An error occurred during registration')
#     context = {"form": form}
#     return render(request, "registration/register.html", context)
#
#
# def logoutPage(request):
#     logout(request)
#     return redirect("/")


def productDetails(request, id):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        itemsCount = 0
        for item in items:
            itemsCount += item.quantity

    else:
        itemsCount = 0

    product = Product.objects.get(id=id)
    context = {"product": product, "itemsCount": itemsCount}
    return render(request, "store/product.html", context)


def error_404_page(request, exception):
    return render(request, "store/404.html")