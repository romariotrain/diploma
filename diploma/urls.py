"""
URL configuration for diploma project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from orders.views import RegisterAccount, PartnerUpdate, AccountDetails, LoginAccount, CategoryView, ShopView, \
    ProductInfoView, BasketView, PartnerState, ContactView, ConfirmAccount

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', RegisterAccount.as_view()),
    path('partner/update/', PartnerUpdate.as_view()),
    path('user/details/', AccountDetails.as_view()),
    path('user/login/', LoginAccount.as_view()),
    path('products/category/', CategoryView.as_view()),
    path('shop/', ShopView.as_view()),
    path('products/info/', ProductInfoView.as_view()),
    path('basket/', BasketView.as_view()),
    path('shop/state/', PartnerState.as_view()),
    path('user/contact/', ContactView.as_view()),
    path('user/confirm/', ConfirmAccount.as_view(),)

]
