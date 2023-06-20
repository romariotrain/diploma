from django.core.mail import send_mail

from diploma import settings

send_mail(
    # title:
    f"Password Reset Token for me",
    # message:
    "it workds",
    # from:
    settings.EMAIL_HOST_USER,
    # to:
    ["romamorozevich@yandex.ru"]
)