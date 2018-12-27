from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render


def login_page(request):

    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'auth/login_page.html', {})

    return render(request, 'auth/login_page.html', {})


@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
