from member.models import Student
from notification.utils import new_notification_count


def add_nav_bar_details(request):
    member = request.user
    if member.is_authenticated and member.is_student:
        try:
            student = member.student
            return {'student_username': member.username,
                    'notifications_count': new_notification_count(student),
                    'student_profile_picture_url': student.get_profile_picture_url()}
        except Student.DoesNotExist:
            return {}
    else:
        return {}
