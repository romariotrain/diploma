import yaml
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
import json
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView
import requests
from orders.forms import CustomUserCreationForm
from orders.models import ProductInfo, Product, Category, Shop, Parameter, ProductParameter, Order, \
    OrderItem, Contact, ConfirmEmailToken
from orders.serializers import CustomUserSerializer, ShopSerializer, CategorySerializer, ProductInfoSerializer, \
    OrderSerializer, ContactSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from orders.mail import send_token_registration, new_order
from drf_spectacular.views import SpectacularAPIView
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from social_django.models import UserSocialAuth


class PartnerUpdate(APIView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:

                response = requests.get(url)

                data = yaml.safe_load(response.content)

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id,)

                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RegisterAccount(CreateAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user_serializer = CustomUserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                password1 = request.data.get('password1')
                password2 = request.data.get('password2')
                user.set_password(password1)
                user.save()
                send_token_registration.delay(user_id=user.id)
                return Response('User registered successfully')
            else:
                return HttpResponse('Не указаны необходимые аргументы')
        else:
            return Response(form.errors)


class ConfirmAccount(APIView):

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return HttpResponse({'detail': 'Аккаунт подтверждён'})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'password1' and 'password2' in request.data:
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            errors = {}
            if password1 == password2:
                try:
                    validate_password(request.data['password1'])
                except Exception as password_error:
                    error_array = []
                    for item in password_error:
                        error_array.append(item)
                    return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
                else:
                    request.user.set_password(request.data['password1'])
            else:
                return HttpResponse('Пароли не совпадают')

        user_serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class LoginAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return Response({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class CategoryView(ListAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    def get(self, request):
        shop_id = request.GET.get('shop_id')
        category_id = request.GET.get('category_id')

        product_infos = ProductInfo.objects.all()
        if shop_id:
            product_infos = product_infos.filter(shop_id=shop_id)
        if category_id:
            product_infos = product_infos.filter(product__category_id=category_id)
        serializer = ProductInfoSerializer(product_infos, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'})

        basket = Order.objects.filter(user=request.user, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.method == 'POST':
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

            items_sting = request.data.get('items')
            if items_sting:
                try:
                    items_dict = json.loads(items_sting)

                except ValueError:
                    return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
                else:
                    basket, _ = Order.objects.get_or_create(user_id=user.id, state='basket')
                    objects_created = 0
                    objects_added = 0
                    for order_item in items_dict:
                        product_info_id = order_item.get('product_info_id')
                        quantity = order_item.get('quantity')
                        if product_info_id and quantity:
                            product_info = get_object_or_404(ProductInfo, id=product_info_id)
                            order_item = OrderItem.objects.filter(order=basket, product_info=product_info).first()
                            if order_item:
                                order_item.quantity += quantity
                                order_item.save()
                                objects_added += 1
                            else:
                                order_item = OrderItem.objects.create(
                                    order=basket,
                                    product_info=product_info,
                                    quantity=quantity,
                                    shop=product_info.shop,
                                )
                                objects_created += 1

                    return Response({'Status': True, 'Создано объектов': objects_created, 'Изменено количество объектов': objects_added})
            return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True
            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return Response({'Status': True, 'Удалено объектов': deleted_count})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=state)
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ContactView(APIView):
    """
    Класс для работы с контактами покупателей
    """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return Response({'Status': True, 'Удалено объектов': deleted_count})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                order = Order.objects.get(id=request.data['id'])
                order_items = order.ordered_items.all()
                for order_item in order_items:
                    product_info = order_item.product_info
                    if product_info:
                        shop = product_info.shop
                        if shop.state:
                            try:
                                is_updated = Order.objects.filter(
                                    user_id=request.user.id, id=request.data['id']).update(
                                    contact_id=request.data['contact'],
                                    state='new')
                            except IntegrityError as error:
                                print(error)
                                return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                            else:
                                if is_updated:
                                    if product_info.quantity < order_item.quantity:
                                        return Response('Товар закончился')
                                    product_info.quantity -= order_item.quantity
                                    product_info.save()
                                    new_order(user_id=request.user.id)
                                    return JsonResponse({'Status': True})
                        else:
                            return Response('Магазин не работает')

            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


def home(request):
    if request.user.is_authenticated:
        try:
            yandex_login = request.user.social_auth.get(provider='yandex-oauth2')
        except UserSocialAuth.DoesNotExist:
            yandex_login = None
        return render(request, 'home.html', {'yandex_login': yandex_login})
    else:
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
