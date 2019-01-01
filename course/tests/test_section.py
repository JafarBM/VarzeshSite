import json

from django.test import TestCase, Client

from course.models import SectionEnrollment
from course.tests.factories import CourseFactory, ChapterFactory, SectionFactory, FeedbackFactory, \
    EnrollmentSectionPassFactory
from exercise.tests.factories import ProblemFactory, SubmissionFactory
from member.tests.factories import MemberFactory


class TestSection(TestCase):
    def test_section_has_passed_preconditions(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)
        section1_1_2 = SectionFactory(chapter=chapter1_1)
        section1_1_2.preconditions.set((section1_1_1,))

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(section1_1_1.has_passed_preconditions(student), False)
        self.assertEqual(section1_1_2.has_passed_preconditions(student), True)
        section1_1_1.pass_for_student(student)
        self.assertEqual(section1_1_1.has_passed_preconditions(student), False)
        self.assertEqual(section1_1_2.has_passed_preconditions(student), False)

    def test_section_is_finished(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        enrollment = course1.enroll(student)
        self.assertEqual(section1_1_1.is_finished(student, enrollment=enrollment), False)
        section1_1_1.pass_for_student(student)
        self.assertEqual(section1_1_1.is_finished(student, enrollment=enrollment), True)

    def test_section_enrollment(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)

        course1.enroll(member.student)
        self.assertEqual(SectionEnrollment.objects.all().count(), 1)

    def test_admin_star_rate(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=2)

        course1.enroll(member.student)

        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                         format(course_slug=course1.slug, chapter_slug=chapter_1_1.slug,
                                section_slug=section_1_1_1.slug))
        black_star_number = response.context['black_star_number']
        self.assertEqual(black_star_number, 1)

    def test_statistic_difficulty(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=4)

        course1.enroll(member.student)
        FeedbackFactory(quality=1, difficulty=1, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=1, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=1, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=1, section=section_1_1_1)

        FeedbackFactory(quality=1, difficulty=2, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=2, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=2, section=section_1_1_1)

        FeedbackFactory(quality=1, difficulty=3, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=3, section=section_1_1_1)
        FeedbackFactory(quality=1, difficulty=3, section=section_1_1_1)

        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/section/statistic/{}'.format(section_1_1_1.id))

        difficulty_grouping = response.context['section'].get_difficulty_grouping()
        self.assertEqual(difficulty_grouping['آسان'], 40)
        self.assertEqual(difficulty_grouping['متوسط'], 30)
        self.assertEqual(difficulty_grouping['سخت'], 30)

    def test_statistic_quality(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=1)

        course1.enroll(member.student)

        for i in range(3):
            FeedbackFactory(quality=i + 1,
                            difficulty=(i + 1 + 2) % 3 + 1,
                            section=section_1_1_1, )
        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/section/statistic/{}'.format(section_1_1_1.id))
        quality_grouping = response.context['section'].get_quality_grouping()

        self.assertEqual(quality_grouping['بد'] * 3, 100)
        self.assertEqual(quality_grouping['متوسط'] * 3, 100)
        self.assertEqual(quality_grouping['خوب'] * 3, 100)

    def test_statistic_averages(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=4)

        FeedbackFactory(quality=1, difficulty=1, section=section_1_1_1, )
        FeedbackFactory(quality=3, difficulty=3, section=section_1_1_1, )
        FeedbackFactory(quality=2, difficulty=1, section=section_1_1_1, )
        FeedbackFactory(quality=2, difficulty=1, section=section_1_1_1, )

        course1.enroll(member.student)

        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/section/statistic/{}'.format(section_1_1_1.id))
        self.assertEqual(response.status_code, 200)
        average_quality = response.context['section'].get_average_quality()
        average_difficulty = response.context['section'].get_average_difficulty()
        self.assertEqual(average_difficulty * 4, 6)
        self.assertEqual(average_quality * 4, 8)

    def test_statistic_passer_count(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)

        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=2)

        for i in range(9):
            member1 = MemberFactory(is_student=True)
            enrollment = course1.enroll(member1.student)
            EnrollmentSectionPassFactory(enrollment=enrollment, section=section_1_1_1)

        for i in range(4):
            member2 = MemberFactory(is_student=True)
            course1.enroll(member2.student)

        course1.enroll(member.student)
        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/section/statistic/{}'.format(section_1_1_1.id))
        self.assertEqual(response.status_code, 200)
        passer_counter = response.context['section'].get_passer_count()
        self.assertEqual(passer_counter, 9)

    def test_enrollment_enddate(self):
        member = MemberFactory(username='username1', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=4)
        enrollment = course1.enroll(member.student)
        self.assertEqual(enrollment.end_date, None)
        c = Client()
        c.login(username='username1', password='havijbastani1')
        section_1_1_1.pass_for_student(member.student)
        enrollment = course1.enroll(member.student)
        self.assertNotEqual(enrollment.end_date, None)

    def test_section_enrollment_for_existed_course(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        SectionFactory(chapter=chapter1_1)
        course1.enroll(member.student)

        SectionFactory(chapter=chapter1_1)
        self.assertEqual(len(SectionEnrollment.objects.filter(student=member.student)), 2)

    def test_slug(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        client = Client()
        client.login(username='username', password='havijbastani1')
        slug = "my-slug"
        slug2 = "my-slug2"
        course1 = CourseFactory(title="course title")
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1, slug=slug)
        self.assertEqual(section1_1_1.slug, slug)
        section1_1_1.slug = slug2
        section1_1_1.save()
        self.assertEqual(section1_1_1.slug, slug2)
        course1.enroll(member.student)
        response = client.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                              format(course_slug=course1.slug, chapter_slug=chapter1_1.slug,
                                     section_slug=section1_1_1.slug))
        self.assertEqual(response.status_code, 200)
        section1_1_2 = SectionFactory(title="title 1", chapter=chapter1_1)
        self.assertEqual(section1_1_2.slug, "title-1")
        section1_1_2.title = "new title 1"
        section1_1_2.save()
        self.assertEqual(section1_1_2.title, "new title 1")
        self.assertEqual(section1_1_2.slug, "title-1")

    def test_section_problem_relation(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory(title="course title")
        chapter1_1 = ChapterFactory(course=course1)
        problem = ProblemFactory()
        submission = SubmissionFactory.create(user=member, problem=problem)
        section1_1_1 = SectionFactory(problem=problem, chapter=chapter1_1)
        course1.enroll(member.student)
        self.assertEqual(section1_1_1.is_finished(member.student), False)
        submission.set_is_correct(True)
        self.assertEqual(section1_1_1.is_finished(member.student), True)
