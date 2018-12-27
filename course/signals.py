from django.db.models.signals import post_save
from django.dispatch import receiver

from course.models import Course, Chapter, Section
from notification.utils import create_course_notification, create_section_notification, create_chapter_notification, \
    notify_new_course, enroll_new_section_for_students


@receiver(post_save, sender=Course, dispatch_uid="my_unique_identifier")
def create_course(sender, instance, created, **kwargs):
    if created:
        create_course_notification(sender, instance)
        notify_new_course(instance)


@receiver(post_save, sender=Chapter, dispatch_uid="my_unique_identifier1")
def create_chapter(sender, instance, created, **kwargs):
    if created:
        create_chapter_notification(sender, instance)


@receiver(post_save, sender=Section, dispatch_uid="my_unique_identifier2")
def create_section(sender, instance, created, **kwargs):
    if created:
        enroll_new_section_for_students(instance)
        create_section_notification(sender, instance)
