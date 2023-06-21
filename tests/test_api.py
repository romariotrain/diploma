from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
import pytest
from rest_framework.authtoken.models import Token

from orders.models import CustomUser, ConfirmEmailToken

factory = APIRequestFactory()
@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return CustomUser.objects.create_user('roman')

@pytest.mark.django_db
def test_register_account(client):
    """
    Test registering a new user account
    """
    url = 'http://127.0.0.1:8000/user/register/'
    user_data = {
        'email': 'korotkovaad@yandex.ru',
        'password1': 'testpassword',
        'password2': 'testpassword',
        'company': 'a',
        'position': 'b'

    }
    response = client.post(url, user_data)
    assert response.status_code == status.HTTP_200_OK





@pytest.mark.django_db
def test_get_user_info():
    user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test_email')
    token = Token.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user=user)
    url = 'http://127.0.0.1/user/details/'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_post_user_info():
    user = CustomUser.objects.create_user(username='testuser', password='testpass', email='test_email')
    token = Token.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user=user)

    user_data = {
        'password1': 'testpassword1',
        'password2': 'testpassword1',

    }

    url = 'http://127.0.0.1/user/details/'
    response = client.post(url, user_data)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_get_products_info():
