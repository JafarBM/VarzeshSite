from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from course.decorators import is_student_check
from notification.notification_proxy import NotificationProxy


@login_required
@user_passes_test(test_func=is_student_check)
def notification_inbox(request):
    member = request.user
    notifications_all = member.notifications.all()
    context = {"notifications": []}
    for notif in notifications_all:
        try:
            myNotif = NotificationProxy(notif)
            context["notifications"].append(myNotif)
            notif.mark_as_read()
        except TypeError:
            continue

    return render(request, 'notification/notifications_list.html', context=context)
