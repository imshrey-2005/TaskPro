from django.core.mail import EmailMessage
from django.conf import settings
class Utils:
    @staticmethod
    def send_email(data):
        email=EmailMessage(subject=data['subject'],
                           body=data['body'],
                           from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                           to=[data['to_email']],)
        email.send()