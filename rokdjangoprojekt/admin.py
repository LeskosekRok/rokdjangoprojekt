# -*- coding: utf-8 -*-
from django.contrib import admin
import smtplib
from email.message import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rokdjangoprojekt.settings import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT

from .models import Ucitelj
from django.contrib.auth.models import User

@admin.action(description="Poslji e-mail za registracijo in reset gesla")
def send_registration_emails(modeladmin, request, queryset):
    for ucitelj in queryset:
        # Poisci uporabnika glede na e-mail
        try:
            user = User.objects.get(email=ucitelj.eposta)
        except User.DoesNotExist:
            # Ce ga ni, ga ustvari
            user = User.objects.create_user(
                username=ucitelj.eposta,
                email=ucitelj.eposta,
                first_name=ucitelj.ime,
                password=User.objects.make_random_password()
            )

        # Generiraj token za ponastavitev gesla
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Link za ponastavitev gesla
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        

        # Poslji e-mail
        username = EMAIL_HOST_USER
        password = EMAIL_HOST_PASSWORD
        msg = EmailMessage()
        msg['Subject'] = "Registracija vasega racuna"
        msg['From'] = username
        msg['To'] = user.email
        msg.set_content(f"Pozdravljeni {user.first_name},\n\n"
                        f"Za nastavitev gesla, kliknite sem: {reset_link}\n\n"
                        f"Hvala!")
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        # send_mail(
        #     subject="Registracija vasega racuna",
        #     message=f"Pozdravljeni {user.first_name},\n\n"
        #             f"Prosimo obiscite {registration_link}, da vidite svoj racun.\n"
        #             f"Za nastavitev gesla, kliknite sem: {reset_link}\n\n"
        #             f"Hvala!",
        #     from_email="admin@django.fbeu.eu",
        #     recipient_list=[user.email],
        # )

class UciteljAdmin(admin.ModelAdmin):
    list_display = ('ime', 'eposta')
    actions = [send_registration_emails]

admin.site.register(Ucitelj, UciteljAdmin)