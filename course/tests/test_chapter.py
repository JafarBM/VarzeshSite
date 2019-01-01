from django.test import Client, TransactionTestCase

from course.tests.factories import CourseFactory, ChapterFactory, SectionFactory, EnrollmentFactory
from member.tests.factories import MemberFactory


class TestChapter(TransactionTestCase):
    def test_get_chapter_list(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course = CourseFactory()

        c = Client()
        c.login(username='username', password='havijbastani1')
        course.enroll(member.student)

        response = c.get('/courses/{course_slug}/chapters/'.format(course_slug=course.slug))
        chapters = response.context['chapters']
        self.assertEqual(len(chapters), 0)

        ChapterFactory(order=0, course=course)
        ChapterFactory(order=1, course=course)

        response = c.get('/courses/{course_slug}/chapters/'.format(course_slug=course.slug))
        chapters = response.context['chapters']
        self.assertEqual(len(chapters), 2)

    def test_chapter_progress(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)

        course1.enroll(member.student)

        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/{course_slug}/chapters/'.format(course_slug=course1.slug))
        chapters = response.context['chapters']
        course1_progress = chapters[chapter_1_1]['progress']
        self.assertEqual(course1_progress, 0)

        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1)
        section_1_1_2 = SectionFactory(order=1, chapter=chapter_1_1)

        section_1_1_1.pass_for_student(member.student)

        response = c.get('/courses/{course_slug}/chapters/'.format(course_slug=course1.slug))
        chapters = response.context['chapters']
        course1_progress = chapters[chapter_1_1]['progress']
        self.assertEqual(course1_progress, 50)

    def test_chapter_is_lock(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)
        chapter1_2 = ChapterFactory(course=course1, preconditions=(chapter1_1,))
        SectionFactory(chapter=chapter1_2)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(chapter1_1.is_lock(student), False)
        self.assertEqual(chapter1_2.is_lock(student), True)
        section1_1_1.pass_for_student(student)
        self.assertEqual(chapter1_1.is_lock(student), False)
        self.assertEqual(chapter1_2.is_lock(student), False)

    def test_chapter_is_finished(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(chapter1_1.is_finished(student), False)
        section1_1_1.pass_for_student(student)
        self.assertEqual(chapter1_1.is_finished(student), True)

    def test_slug(self):
        slug = "my-slug"
        slug2 = "my-slug2"
        course1 = CourseFactory(title="course title")
        chapter1_1 = ChapterFactory(course=course1, slug=slug)
        self.assertEqual(chapter1_1.slug, slug)
        chapter1_1.slug = slug2
        chapter1_1.save()
        self.assertEqual(chapter1_1.slug, slug2)
        chapter1_2 = ChapterFactory(title="title 1", course=course1)
        self.assertEqual(chapter1_2.slug, "title-1")
        chapter1_2.title = "new title 1"
        chapter1_2.save()
        self.assertEqual(chapter1_2.title, "new title 1")
        self.assertEqual(chapter1_2.slug, "title-1")