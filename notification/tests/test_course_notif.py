from unittest import mock

from django.test import TestCase

from course.tests.factories import CourseFactory


class TestCourseNotificationSignal(TestCase):
    def test_course_creation_notification(self):
        with mock.patch('course.signals.create_course_notification', autospec=True) as mocked_handler:
            course1 = CourseFactory()
            course1.save()

            self.assertEquals(mocked_handler.call_count, 1)
