from orders.models import CustomUser

user = CustomUser.objects.get(email='admin@mail.ru')
print(user)
