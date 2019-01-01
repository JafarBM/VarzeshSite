from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task()
def celery_send_mail(subject, text, to):
    email = EmailMessage(subject, text, to=[to])
    email.content_subtype = 'html'
    return bool(email.send())


def send_mail(subject, text, to):
    return celery_send_mail.delay(subject, text, to)
