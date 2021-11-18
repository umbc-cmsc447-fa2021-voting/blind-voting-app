from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.CharField(max_length=50, blank=True)
    ssn = models.CharField(max_length=20, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)

        token = default_token_generator.make_token(user=instance)
        uid = urlsafe_base64_encode(str(instance.pk).encode())
        reset_url = reverse('password_reset_confirm', kwargs={ 'token': token, 'uidb64': uid })
        url = f'{settings.DEFAULT_DOMAIN}{reset_url}'
        if instance.email:
            send_mail(
                'Blind Voting App - Account Created',
                f'An account for you has been created under the username "{instance.username}"!\nPlease set a password for your new account by visiting the following URL: {url}',
                None,
                [instance.email],
                fail_silently=True
            )

@receiver(post_save, sender=User)
def save_user(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    if instance.email:
        send_mail(
            'Blind Voting App - Account Deleted',
            f'The account named "{instance.username}" associated with this email has been deleted.',
            None,
            [instance.email],
            fail_silently=True
        )
