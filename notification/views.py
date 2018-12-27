import ast

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from course.utils import is_student_check, add_navbar_data_context
from notification.utils import new_notification_check


@login_required
@user_passes_test(test_func=is_student_check)
def notification_inbox(request):
    member = request.user
    student = member.student
    context = {"notifications": []}
    unread_notifications = member.notifications.unread()
    for notif in member.notifications.all():
        try:
            context["notifications"].append(
                {"verb": notif.verb,
                 "description": notif.description,
                 "link": ast.literal_eval(notif.data['data'])['link'],
                 "target": notif.target.logo_url(),
                 "is_unread": True if notif in unread_notifications else False}
            )
            notif.mark_as_read()
        except TypeError:
            continue

    context = add_navbar_data_context(student_username=member.username,
                                      notification_count=new_notification_check(student),
                                      student=student,
                                      context=context)

    return render(request, 'notification/notifications_list.html', context=context)
