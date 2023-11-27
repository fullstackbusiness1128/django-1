from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings


def verify_user(backend, user, response, *args, **kwargs):
    if backend.name == 'linkedin-oauth2':
        user.is_verified = True
        if kwargs["is_new"]:
            user.linkedin = f'https://www.linkedin.com/in/?uid={kwargs["uid"]}'
            message = render_to_string('payment_success_email.html', {'link': reverse('signup')})
            send_mail(
                'Welcome to Leader Terminal',
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=message,
                fail_silently=True
            )
        user.save()
