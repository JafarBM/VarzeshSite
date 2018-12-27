from datetime import timedelta

from .constants import WEEKENDS


def is_same(a, b):
    return abs(a - b) < 1e-9


def merge_dictionaries(**kwargs):
    result = {}
    for base_course in list(kwargs.values())[0]:
        result[base_course] = {key: value[base_course] for key, value in kwargs.items()}
    return result


def workdays_between_count(from_date, to_date):
    day_generator = (from_date + timedelta(x + 1) for x in range((to_date - from_date).days))
    return sum(1 for day in day_generator if day.weekday() not in WEEKENDS)


def is_student_check(user):
    return user.is_student


def add_navbar_data_context(student_username, notification_count,
                            student, context):
    context['student_username'] = student_username
    context['notification_count'] = notification_count
    context['student_profile_picture_url'] = student.get_profile_picture_url()
    return context
