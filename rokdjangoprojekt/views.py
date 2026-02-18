from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import UciteljNaSoli
from .models import Ucitelj
from .models import Sola

def profile(request):
    email = request.user.email
    sole = Sola.objects.filter(uciteljnasoli__id_ucitelj__eposta=email).distinct()
    return render(request, "profile.html", {"sole": sole})

