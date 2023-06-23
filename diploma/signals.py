from django.contrib.auth.models import User
from django.dispatch import receiver
from social_django.signals import socialauth_registered

from orders.models import CustomUser
from rest_framework.response import Response

@receiver(socialauth_registered)
def social_auth_user_created_handler(sender, user, response, details, **kwargs):
    # Ищем пользователя в базе данных по адресу электронной почте
    email = details.get('email', '')
    existing_user = CustomUser.objects.filter(email=email)
    if not existing_user:
        return Response("Пользователь с такой электронной почтой не найден")

        # Обновляем значение поля is_active для найденного пользователей
    for existing_user in existing_user:
        existing_user.is_active = True
        existing_user.save()
        return email
