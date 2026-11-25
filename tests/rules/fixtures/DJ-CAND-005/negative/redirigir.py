from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


def ir(request):
    if request.user.is_authenticated:
        return redirect("/inicio")
    return HttpResponseRedirect(reverse("login"))
