from unittest import mock

from django.test import TestCase

from course.tests.factories import ChapterFactory, CourseFactory, SectionFactory


class TestSectionNotificationSignal(TestCase):
    def test_section_creation_notification(self):
        with mock.patch('course.signals.create_section_notification', autospec=True) as mocked_handler:
            course1 = CourseFactory()
            course1.save()
            chap1 = ChapterFactory(course=course1)
            chap1.save()
            section1 = SectionFactory(chapter=chap1)
            section1.save()

            self.assertEquals(mocked_handler.call_count, 1)
