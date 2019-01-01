from django import template

from course.constants import MAX_SECTION_RATE
from course.models import Enrollment

register = template.Library()


@register.filter(name='get_keys_list')
def get_keys_list(dictionary):
    return list(*dictionary)


@register.filter(name='get_key')
def get_key(dictionary, key):
    return dictionary[key]


@register.simple_tag
def course_can_enroll(course, student):
    enrollment = Enrollment.objects.filter(course=course, student=student)
    if enrollment:
        return False
    return True


@register.simple_tag
def course_is_locked(course, student):
    return course.is_lock(student)


@register.simple_tag
def get_course_progress(course, student):
    return course.get_course_progress(student)


@register.simple_tag
def is_available(enrollment, section):
    if section is None:
        return False
    return enrollment.is_section_available(section)


@register.simple_tag
def has_used_credit(enrollment, section):
    return enrollment.has_used_credit(section)


@register.simple_tag
def is_finished(section, student, enrollment):
    return section.is_finished(student, enrollment)


@register.simple_tag
def get_black_star_number(section):
    return MAX_SECTION_RATE - section.admin_rate


@register.simple_tag
def get_max_section_rate():
    return MAX_SECTION_RATE


@register.simple_tag
def get_previous(section):
    return section.get_previous_section()


@register.simple_tag
def get_previous(section):
    return section.get_next_section()


@register.filter()
def get_student_rank(course, enrolment):
    return course.get_student_rank_percentile(enrolment)
