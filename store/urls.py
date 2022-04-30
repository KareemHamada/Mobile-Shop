from django.urls import path,include

from . import views

urlpatterns =[
	path("",views.store,name="store"),
	path("cart/",views.cart,name="cart"),
	path("checkout/",views.checkout,name="checkout"),
	path("updateItem/",views.updateItem,name="updateItem"),
	#path("loginPage/",views.loginPage,name="loginPage"),
	#path("registerPage/",views.registerPage,name="registerPage"),
	#path("logoutPage/",views.logoutPage,name="logoutPage"),
	path("product/<str:id>/",views.productDetails,name="productDetails"),
]
