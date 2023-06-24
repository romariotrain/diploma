
from orders.models import CustomUser
from orders.mail import password_mail


def check_email(backend, details, response, *args, **kwargs):
    email = details.get('email')
    if email:
        # Check if a user with this email already exists
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            # Create a new user with the given email
            user = CustomUser.objects.create_user(email=email, password=CustomUser.objects.make_random_password(),
                                                  username=email.split('@')[0], is_active=True)
            password_mail.delay(user_id=user.id, password=user.password)
        else:
            user.is_active=True
            user.save()
            password_mail.delay(user_id=user.id, password=user.password)
    else:
        # Email is not provided, raise an exception or return an error message
        raise ValueError('Email is required')

    # Return the user object to continue the authentication process
    return {'user': user}