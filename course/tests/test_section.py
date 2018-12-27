from django.test import TestCase, Client

from course.models import SectionEnrollment
from course.tests.factories import CourseFactory, ChapterFactory, SectionFactory, FeedbackFactory, \
    EnrollmentSectionPassFactory
from member.tests.factories import MemberFactory


class TestSection(TestCase):
    def test_section_is_lock(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)
        section1_1_2 = SectionFactory(chapter=chapter1_1)
        section1_1_2.preconditions.set((section1_1_1,))

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(section1_1_1.is_lock(student), False)
        self.assertEqual(section1_1_2.is_lock(student), True)
        section1_1_1.pass_for_student(student)
        self.assertEqual(section1_1_1.is_lock(student), False)
        self.assertEqual(section1_1_2.is_lock(student), False)

    def test_section_is_finished(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(section1_1_1.is_finished(student), False)
        section1_1_1.pass_for_student(student)
        self.assertEqual(section1_1_1.is_finished(student), True)

    def test_section_enrollment(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

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

        orange_star_number = response.context['orange_star_number']
        black_star_number = response.context['black_star_number']
        self.assertEqual(orange_star_number, 2)
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

        response = c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                         format(course_slug=course1.slug, chapter_slug=chapter_1_1.slug,
                                section_slug=section_1_1_1.slug))

        difficulty_grouping = response.context['difficulty_grouping']
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

        response = c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                         format(course_slug=course1.slug, chapter_slug=chapter_1_1.slug,
                                section_slug=section_1_1_1.slug))

        quality_grouping = response.context['quality_grouping']
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

        response = c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                         format(course_slug=course1.slug, chapter_slug=chapter_1_1.slug,
                                section_slug=section_1_1_1.slug))

        average_quality = response.context['average_quality']
        average_difficulty = response.context['average_difficulty']
        self.assertEqual(average_difficulty * 4, 6)
        self.assertEqual(average_quality * 4, 8)

    def test_statistic_passer_count(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)

        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, admin_rate=4)

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

        response = c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}'.
                         format(course_slug=course1.slug, chapter_slug=chapter_1_1.slug,
                                section_slug=section_1_1_1.slug))

        passer_counter = response.context['passer_count']
        self.assertEqual(passer_counter, 9)

    def test_section_enrollment_for_existed_course(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section_1_1_1 = SectionFactory(chapter=chapter1_1)
        course1.enroll(member.student)

        section_1_1_2 = SectionFactory(chapter=chapter1_1)
        self.assertEqual(len(SectionEnrollment.objects.filter(student=member.student)), 2)
