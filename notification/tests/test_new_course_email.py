from unittest import mock

from django.test import TestCase

from course.tests.factories import CourseFactory


class TestCourseEmailSignal(TestCase):
    def test_course_creation_email(self):
        with mock.patch('course.signals.notify_new_course', autospec=True) as mocked_handler:
            course1 = CourseFactory()
            course1.save()

            self.assertEquals(mocked_handler.call_count, 1)
