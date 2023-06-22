from unittest import TestCase

import psycopg2
import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from model_bakery import baker

from orders.models import CustomUser, Shop, ProductInfo, OrderItem, Order, Category, Product

factory = APIRequestFactory()


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture(scope='module')
def db_conn():
    conn = psycopg2.connect(
        dbname='orders',
        user='postgres',
        password='1234',
        host='127.0.0.1',
        port='5431'
    )
    yield conn
    conn.close()


@pytest.fixture
def user():
    user = CustomUser.objects.create(
     email= "romamorozevich@yandex.ru",
     username= "nnk2",
     company= "roma_company",
     position= "manager",

    )
    return user



@pytest.fixture
def shop_factory():
    def factory(*args, **kwargs):
        return baker.make(Shop, *args, **kwargs)

    return factory


@pytest.fixture
def products_factory():
    def factory(*args, **kwargs):
        return baker.make(ProductInfo, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_register_account(client):

    url = 'http://127.0.0.1:8000/user/register/'
    user_data = {
        'email': 'kor@yandex.ru',
        'password1': 'testpassword',
        'password2': 'testpassword',
        'company': 'a',
        'position': 'b'

    }
    response = client.post(url, user_data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_user_info(client):
    user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test_email')
    client.force_authenticate(user=user)
    url = 'http://127.0.0.1/user/details/'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_user_info(client):
    user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test_email')
    client.force_authenticate(user=user)

    user_data = {
        'password1': 'testpassword1',
        'password2': 'testpassword1',

    }

    url = 'http://127.0.0.1/user/details/'
    response = client.post(url, user_data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_products_info(client):
    response1 = client.get('http://127.0.0.1:8000/products/info/')
    # response2 = client.get('http://127.0.0.1:8000/products/info?shop_id=11')
    assert response1.status_code == status.HTTP_200_OK
    # assert response2.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_shop(client, shop_factory):
    shops = shop_factory(_quantity=10)
    response = client.get("http://127.0.0.1:8000/shops/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(shops)


@pytest.mark.django_db
def test_get_category(client):
    response = client.get("http://127.0.0.1:8000/products/category/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_basket_info(client):
    user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test_email')
    client.force_authenticate(user=user)
    url = 'http://127.0.0.1/user/basket/'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_all_products(db_conn, client):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM product_info')
    results = cursor.fetchall()
    assert len(results) == 8

@pytest.mark.django_db
def test_product_info(client,user):
    print(user)

    shop = Shop.objects.create(
        name='My Shop',
        user=user,
        state=True,
    )

    product_info = ProductInfo.objects.create(
        model='Model A',
        product_id=1,
        shop=shop,
        name='Product Name',
        quantity=10,
        price=99.99,
        price_rrc=109.99,
        external_id=12345
    )

    basket = Order.objects.create(user_id=user.id, state='basket')

    order_item = OrderItem.objects.create(
        order=basket,
        product_info=product_info,
        quantity=10,
        shop=shop,
    )

    category_object = Category.objects.create(id=1, name='name')
    category_object.shops.add(shop.id)
    product_item = Product.objects.create(category=category_object, name='product_name')

    client.force_authenticate(user=user)
    response = client.post('http://127.0.0.1:8000/user/basket/', {'items' : "[{\"product_info_id\": 1, \"quantity\": 1}]"})
    assert response.status_code == 200
    assert product_info.product_id == product_item.id


