from django.conf.urls import url

from . import views

urlpatterns = [
    url('login/', views.login_page, name='login_page')
]
