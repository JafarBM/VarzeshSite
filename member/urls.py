from django.urls import path, include

from member.views import credit_log

app_name = ''

urlpatterns = [
    path('', include('registration.backends.simple.urls')),
    path('credit-logs', credit_log, name='credit_log')
]
