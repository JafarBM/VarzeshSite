from django.contrib import admin
from notifications.models import Notification

admin.site.unregister(Notification)

