import json

from django.conf import settings
from django.template.loader import get_template
from notifications.signals import notify

from course.models import Enrollment, SectionEnrollment
from member.models import Member
from .tasks import send_mail


def notify_new_course(course):
    if not settings.SEND_EMAIL_NEW_COURSE:
        return
    mail_subject = 'اضافه شدن درس جدید!'
    message = get_template('course/new_course_email.html').render({
        'course': course,
        'cover': settings.SITE_URL + course.cover_url()
    })
    users_email = Member.objects.values_list("email")
    for user_email in users_email:
        email = user_email[0]
        send_mail(mail_subject, message, email)


def create_course_notification(actor, created_course):
    recipients = Member.objects.prefetch_related('student').filter(is_student=True)
    for recipient in recipients:
        if not created_course.is_lock(student=recipient.student):
            description = "اسم درس: " + created_course.title
            data = json.dumps({"link": "/courses/" + str(created_course.slug) + "/chapters/"})
            notify.send(target=created_course,
                        sender=actor,
                        recipient=recipient,
                        verb="درس جدیدی اضافه شده",
                        description=description,
                        data=data)


def create_chapter_notification(actor, created_chapter):
    recipients = Member.objects.prefetch_related('student').filter(is_student=True)
    for recipient in recipients:
        if Enrollment.objects.filter(course=created_chapter.course, student=recipient.student):
            if not created_chapter.is_lock(student=recipient.student):
                description = "اسم فصل: " + created_chapter.title
                data = json.dumps({'link': '/courses/' + str(created_chapter.course.slug) + '/chapters/'})
                notify.send(target=created_chapter,
                            sender=actor,
                            recipient=recipient,
                            verb="فصل جدیدی به درست اضافه شده",
                            description=description,
                            data=data, EXTRA_DATA=True)


def create_section_notification(actor, created_section):
    recipients = Member.objects.prefetch_related('student').filter(is_student=True)
    for recipient in recipients:
        if created_section in SectionEnrollment.objects.filter(student=recipient.student):
            if not created_section.has_passed_preconditions(student=recipient.student):
                description = "اسم بخش: " + created_section.title
                data = json.dumps({'link': '/courses/' + str(created_section.chapter.course.slug) + '/chapters/' + str(
                    created_section.chapter.slug) + '/sections/' + str(created_section.slug)})
                notify.send(target=created_section,
                            sender=actor,
                            recipient=recipient,
                            verb="بخش جدیدی به درست اضافه شده",
                            description=description,
                            data=data)


def enroll_new_section_for_students(section):
    enrollments = Enrollment.objects.filter(course=section.chapter.course)
    for enrollment in enrollments:
        section.enroll(enrollment.student)


def new_notification_count(student):
    return student.member.notifications.unread().count()
