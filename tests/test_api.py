import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from model_bakery import baker

from orders.models import CustomUser, Shop, ProductInfo

factory = APIRequestFactory()


@pytest.fixture
def client():
    return APIClient()


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