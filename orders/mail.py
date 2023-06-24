from django.conf import settings
from orders.models import ConfirmEmailToken, CustomUser
from celery import shared_task

from django.core.mail import send_mail
from django.conf import settings


@shared_task
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    subject = f"Password Reset Token for {reset_password_token.user}"
    message = reset_password_token.key
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [reset_password_token.user.email]
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_token_registration(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    
    send_mail(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )



@shared_task
def new_order(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """

    user = CustomUser.objects.get(id=user_id)

    send_mail(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )


@shared_task
def password_mail(user_id, password, **kwargs):
    """
    отправяем письмо с паролем при регистрации через социальную сеть. Нужно буде с паролем залогиниться, что
    бы получить токен
    """

    user = CustomUser.objects.get(id=user_id)

    send_mail(
        # title:
        f"токен",
        # message:
        f"password: {password}",
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )

