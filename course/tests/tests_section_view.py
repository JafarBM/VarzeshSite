from django.test import TestCase
from django.urls import reverse

from course.models import SectionEnrollment
from .factories import SectionFactory, ChapterFactory, MemberFactory, EnrollmentSectionPassFactory


class SectionDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory(username='danial', password='havijbastani1', is_student=True)

        cls.parent_chapter = ChapterFactory()

    def setUp(self):
        # Needs minimum of 3 to test previous and next
        self.sections_per_chapter = 4
        self.sections = [SectionFactory(chapter=self.parent_chapter) for _ in range(self.sections_per_chapter)]
        self.student = self.member.student

        self.client.login(username=self.member.username, password='havijbastani1')
        self.enrollment = self.parent_chapter.course.enroll(self.student)

    def test_details(self):
        # Middle of list to definitely have previous and next
        test_section = self.sections[self.sections_per_chapter // 2]
        section_detail_url = '/courses/{}/chapters/{}/sections/{}'.format(self.parent_chapter.course.slug,
                                                                          self.parent_chapter.slug,
                                                                          test_section.slug)

        response = self.client.get(section_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['section'])
        self.assertIsNotNone(response.context['previous_section'])
        self.assertIsNotNone(response.context['next_section'])

    def test_is_none_for_no_previous(self):
        test_section = self.sections[0]
        response = self.client.get(
            reverse('course:section-detail', kwargs={'course_slug': self.parent_chapter.course.slug,
                                                     'chapter_slug': self.parent_chapter.slug,
                                                     'section_slug': test_section.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['section'])
        self.assertIsNone(response.context['previous_section'])

        self.assertIsNotNone(response.context['next_section'])

    def test_is_none_for_no_next(self):
        test_section = self.sections[self.sections_per_chapter - 1]
        response = self.client.get(
            reverse('course:section-detail', kwargs={'course_slug': self.parent_chapter.course.slug,
                                                     'chapter_slug': self.parent_chapter.slug,
                                                     'section_slug': test_section.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['section'])
        self.assertIsNotNone(response.context['previous_section'])
        self.assertIsNone(response.context['next_section'])

    def test_is_section_locked(self):
        test_section = self.sections[2]
        test_section_pre1 = self.sections[0]
        test_section_pre2 = self.sections[1]
        test_section.preconditions.add(test_section_pre1, test_section_pre2)

        response = self.client.get(
            reverse('course:section-detail', kwargs={'course_slug': self.parent_chapter.course.slug,
                                                     'chapter_slug': self.parent_chapter.slug,
                                                     'section_slug': test_section.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course/section-detail.html')
        self.assertContains(response, "این قسمت برای شما موجود نمی باشد")

    def test_is_section_unlocked(self):
        test_section = self.sections[2]
        test_section_pre1 = self.sections[0]
        test_section_pre2 = self.sections[1]
        test_section.preconditions.add(test_section_pre1, test_section_pre2)
        test_section_pre1_pass_section = EnrollmentSectionPassFactory(enrollment=self.enrollment,
                                                                      section=test_section_pre1)
        test_section_pre2_pass_section = EnrollmentSectionPassFactory(enrollment=self.enrollment,
                                                                      section=test_section_pre2)

        response = self.client.get(
            reverse('course:section-detail', kwargs={'course_slug': self.parent_chapter.course.slug,
                                                     'chapter_slug': self.parent_chapter.slug,
                                                     'section_slug': test_section.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course/section-detail.html')
        self.assertNotContains(response, "این قسمت برای شما موجود نمی باشد")

    def test_is_section_passed_after_pass_request(self):
        test_section = self.sections[0]
        test_section.pass_for_student(self.student)
        self.assertEqual(self.enrollment.passed_sections.count(), 1)

    def test_is_locked_section_not_passed_after_pass_request(self):
        test_section = self.sections[1]
        test_section_pre = self.sections[0]
        test_section.preconditions.add(test_section_pre)
        test_section.pass_for_student(self.student)
        self.assertEqual(self.enrollment.passed_sections.count(), 0)

    def test_start_time_first_visit(self):
        test_section = self.sections[0]
        section_pass_url = '/courses/{}/chapters/{}/sections/{}/pass'.format(self.parent_chapter.course.slug,
                                                                             self.parent_chapter.slug,
                                                                             test_section.slug)

        student = self.student
        self.parent_chapter.course.enroll(student)
        default_start_time = SectionEnrollment.objects.get(section=test_section, student=student)
        response = self.client.get(section_pass_url)
        self.assertIsNot(SectionEnrollment.objects.get(section=test_section, student=student).started_time,
                         default_start_time)

    def test_section_submit_feedback_url(self):
        test_section = self.sections[0]
        section_submit_feedback_url = '/courses/{}/chapters/{}/sections/{}/submit_feedback'.format(
            self.parent_chapter.course.slug,
            self.parent_chapter.slug,
            test_section.slug)

        response = self.client.get(section_submit_feedback_url)
        # returns redirect
        self.assertEqual(response.status_code, 302)

    def test_passed_section_feedback_submitted_after_request(self):
        test_section = self.sections[0]
        test_section.pass_for_student(self.student)

        data = {"comment": "test text", "quality": 1, "difficulty": 1}

        self.client.post(reverse('course:section-submit-feedback',
                                 kwargs={'course_slug': self.parent_chapter.course.slug,
                                         'chapter_slug': self.parent_chapter.slug,
                                         'section_slug': test_section.slug}), data=data)

        self.assertEqual(self.student.feedback_set.count(), 1)
        self.assertEqual(self.student.feedback_set.first().comment, data['comment'])
        self.assertEqual(self.student.feedback_set.first().quality, data['quality'])
        self.assertEqual(self.student.feedback_set.first().difficulty, data['difficulty'])

    def test_not_passed_section_feedback_not_submitted_after_request(self):
        test_section = self.sections[0]

        data = {"comment": "test text", "quality": 1, "difficulty": 1}

        self.client.post(reverse('course:section-submit-feedback',
                                 kwargs={'course_slug': self.parent_chapter.course.slug,
                                         'chapter_slug': self.parent_chapter.slug,
                                         'section_slug': test_section.slug}), data=data)

        self.assertEqual(self.student.feedback_set.count(), 0)

    def test_redirect_if_section_is_not_locked(self):
        test_section = SectionFactory(chapter=self.parent_chapter, credit=-10)

        section_unlock_url = '/courses/{}/chapters/{}/sections/{}/use-credit'.format(self.parent_chapter.course.slug,
                                                                                     self.parent_chapter.slug,
                                                                                     test_section.slug)

        response = self.client.post(section_unlock_url)
        self.assertEqual(response.status_code, 302)

    def test_not_create_log_insufficient_credit(self):
        student_credit = self.student.compute_credit()
        test_section = SectionFactory.create(chapter=self.parent_chapter, credit=10, preconditions=(self.sections[0],))

        section_unlock_url = '/courses/{}/chapters/{}/sections/{}/use-credit'.format(self.parent_chapter.course.slug,
                                                                                     self.parent_chapter.slug,
                                                                                     test_section.slug)
        response = self.client.post(section_unlock_url)
        self.assertEqual(self.student.compute_credit(), student_credit)
        self.assertEqual(response.status_code, 200)

    def test_create_log_sufficient_credit(self):
        student_credit = self.student.compute_credit()
        test_section = SectionFactory.create(chapter=self.parent_chapter, credit=-10, preconditions=(self.sections[0],))

        section_unlock_url = '/courses/{}/chapters/{}/sections/{}/use-credit'.format(self.parent_chapter.course.slug,
                                                                                     self.parent_chapter.slug,
                                                                                     test_section.slug)
        response = self.client.post(section_unlock_url)
        self.assertEqual(self.student.compute_credit(), student_credit - test_section.credit)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(test_section.credit_logs.all()), 1)

    def test_unique_create_log(self):
        test_section = SectionFactory.create(chapter=self.parent_chapter, credit=-10, preconditions=(self.sections[0],))

        section_unlock_url = '/courses/{}/chapters/{}/sections/{}/use-credit'.format(self.parent_chapter.course.slug,
                                                                                     self.parent_chapter.slug,
                                                                                     test_section.slug)
        self.client.post(section_unlock_url)
        student_credit = self.student.compute_credit()
        response = self.client.post(section_unlock_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(student_credit, self.student.compute_credit())
        self.assertEqual(len(test_section.credit_logs.all()), 1)

    def test_unlock_section_after_use_credit(self):
        test_section = SectionFactory.create(chapter=self.parent_chapter, credit=-10, preconditions=(self.sections[0],))

        section_unlock_url = '/courses/{}/chapters/{}/sections/{}/use-credit'.format(self.parent_chapter.course.slug,
                                                                                     self.parent_chapter.slug,
                                                                                     test_section.slug)
        section_detail_url = '/courses/{}/chapters/{}/sections/{}'.format(self.parent_chapter.course.slug,
                                                                          self.parent_chapter.slug,
                                                                          test_section.slug)

        self.client.post(section_unlock_url)
        self.client.post(section_detail_url)
        self.assertEqual(test_section in self.enrollment.unlocked_sections.all(), True)

    def test_unlock_function(self):
        test_section = SectionFactory.create(chapter=self.parent_chapter, credit=-10, preconditions=(self.sections[0],))
        self.enrollment.unlocked_sections.add(test_section)
        self.assertEqual(len(self.enrollment.unlocked_sections.all()), 1)
