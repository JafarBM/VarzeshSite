from unittest import mock

from django.test import TestCase

from course.tests.factories import ChapterFactory, CourseFactory


class TestChapterNotificationSignal(TestCase):
    def test_chapter_creation_notification(self):
        with mock.patch('course.signals.create_chapter_notification', autospec=True) as mocked_handler:
            course1 = CourseFactory()
            course1.save()
            chap1 = ChapterFactory(course=course1)
            chap1.save()

            self.assertEquals(mocked_handler.call_count, 1)
