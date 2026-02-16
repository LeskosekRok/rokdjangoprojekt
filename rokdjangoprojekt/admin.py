# -*- coding: utf-8 -*-
from django.contrib import admin, messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import Ucitelj
from django.contrib.auth.models import User
import traceback

@admin.action(description="Pošlji e-mail za registracijo in reset gesla")
def send_registration_emails(modeladmin, request, queryset):
    for ucitelj in queryset:
        try:
            email = (ucitelj.eposta or "").strip()
            first_name = (ucitelj.ime or "").strip()

            if not email:
                messages.error(request, f"Ucitelj '{first_name}' nima e-pošte.")
                continue

            # Try to find existing user
            user_qs = User.objects.filter(email=email)
            if user_qs.exists():
                user = user_qs.first()
            else:
                # Ensure username is non-empty and unique
                username = email if email else User.objects.make_random_password()
                while User.objects.filter(username=username).exists():
                    username = User.objects.make_random_password()
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    password=User.objects.make_random_password()
                )

            # Generate token for password reset
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset and registration links
            reset_link = f"https://django.fbeu.eu/reset/{uid}/{token}/"
            registration_link = f"https://django.fbeu.eu/welcome?email={user.email}"

            # Send email safely
            try:
                send_mail(
                    subject="Registracija vašega računa",
                    message=f"Pozdravljeni {user.first_name},\n\n"
                            f"Prosimo obiščite {registration_link}, da vidite svoj račun.\n"
                            f"Za nastavitev gesla, kliknite sem: {reset_link}\n\n"
                            f"Hvala!",
                    from_email="admin@django.fbeu.eu",
                    recipient_list=[user.email],
                    fail_silently=False
                )
                messages.success(request, f"E-mail poslan uporabniku '{user.email}'.")
            except Exception as email_error:
                messages.error(request, f"Napaka pri pošiljanju e-maila '{user.email}': {email_error}")

        except Exception as e:
            messages.error(request, f"Napaka pri obdelavi '{ucitelj.ime}': {traceback.format_exc()}")

class UciteljAdmin(admin.ModelAdmin):
    list_display = ('ime', 'eposta')
    actions = [send_registration_emails]

admin.site.register(Ucitelj, UciteljAdmin)
