from django.test import Client, TransactionTestCase

from course.models import Course, Enrollment, TagScore
from course.tests.factories import CourseFactory, ChapterFactory, SectionFactory, CategoryFactory, \
    TagFactory, RecommendationTagFactory
from exercise.tests.factories import ProblemFactory
from member.tests.factories import MemberFactory


class TestCourse(TransactionTestCase):
    def test_course_creation_success(self):
        course1 = CourseFactory()
        course2 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        chapter_1_2 = ChapterFactory(order=1, course=course1)
        chapter_2_1 = ChapterFactory(order=0, course=course2)
        chapter_2_2 = ChapterFactory(order=1, course=course2)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1, problem=ProblemFactory.create(course=course1))
        section_1_1_2 = SectionFactory(order=1, chapter=chapter_1_1, problem=ProblemFactory.create(course=course1))
        section_2_1_1 = SectionFactory(order=0, chapter=chapter_2_1, problem=ProblemFactory.create(course=course2))
        section_2_1_2 = SectionFactory(order=1, chapter=chapter_2_1, problem=ProblemFactory.create(course=course2))
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(course1.chapter_set.count(), 2)
        self.assertEqual(chapter_1_1.sections.count(), 2)
        self.assertEqual(chapter_2_2.sections.count(), 0)

    def test_get_courses_list(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        course2 = CourseFactory()
        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/')
        courses = response.context['courses']
        self.assertEqual(len(courses), 2)

    def test_get_courses_list_by_category(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        category1 = CategoryFactory()
        category2 = CategoryFactory()
        course1 = CourseFactory(categories=(category1,))
        course2 = CourseFactory()
        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/?category_id={category_id}'.format(category_id=category1.id))
        courses = response.context['courses']
        self.assertEqual(len(courses), 1)
        response = c.get('/courses/?category_id={category_id}'.format(category_id=category2.id))
        courses = response.context['courses']
        self.assertEqual(len(courses), 0)

    def test_course_progress(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student
        course1 = CourseFactory()
        chapter_1_1 = ChapterFactory(order=0, course=course1)
        chapter_1_2 = ChapterFactory(order=1, course=course1)
        section_1_1_1 = SectionFactory(order=0, chapter=chapter_1_1)
        SectionFactory(order=1, chapter=chapter_1_1)
        SectionFactory(order=0, chapter=chapter_1_2)
        SectionFactory(order=1, chapter=chapter_1_2)
        course1.enroll(student)
        section_1_1_1.pass_for_student(student)
        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/')
        courses = response.context['courses']
        course1_progress = courses[0].get_course_progress(student)
        self.assertEqual(course1_progress, 25)

    def test_course_lock(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        course2 = CourseFactory(preconditions=(course1,))

        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/')
        courses = response.context['courses']

        course1_lock = courses[0].is_lock(student=member.student)
        course2_lock = courses[1].is_lock(student=member.student)

        self.assertEqual(course1_lock, False)
        self.assertEqual(course2_lock, True)

    def test_course_is_lock(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course2 = CourseFactory(preconditions=(course1,))

        course1.enroll(student)
        self.assertEqual(course2.is_lock(student), True)
        self.assertEqual(course1.is_lock(student), False)
        section1_1_1.pass_for_student(student)
        self.assertEqual(course2.is_lock(student), False)
        self.assertEqual(course1.is_lock(student), False)

    def test_course_enroll(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        c = Client()
        c.login(username='username', password='havijbastani1')
        c.post('/courses/{course_slug}/enroll/'.format(course_slug=course1.slug))
        self.assertEqual(Enrollment.objects.filter(student=member.student, course=course1).count(), 1)

    def test_course_enroll_unique(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        course1.enroll(member.student)
        c = Client()
        c.login(username='username', password='havijbastani1')
        c.post('/courses/{course_slug}/enroll/'.format(course_slug=course1.slug))
        self.assertEqual(Enrollment.objects.filter(student=member.student, course=course1).count(), 1)

    def test_course_can_enroll(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()

        c = Client()
        c.login(username='username', password='havijbastani1')

        response = c.get('/courses/')
        courses = response.context['courses']
        can_enroll = False if Enrollment.objects.filter(course=courses[0], student=member.student) else True
        self.assertEqual(can_enroll, True)

        course1.enroll(member.student)

        response = c.get('/courses/')
        courses = response.context['courses']
        can_enroll = False if Enrollment.objects.filter(course=courses[0], student=member.student) else True
        self.assertEqual(can_enroll, False)

    def test_get_tags(self):
        MemberFactory(username='username', password='havijbastani1', is_student=True)
        tag0 = TagFactory()
        tag1 = TagFactory()
        tag2 = TagFactory()

        course1 = CourseFactory()
        chapter1 = ChapterFactory(course=course1)
        SectionFactory(chapter=chapter1, tags=(tag0, tag1))
        SectionFactory(chapter=chapter1, tags=(tag0, tag2))
        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/')
        courses = response.context['courses']
        tags = courses[0].get_tags()
        self.assertEqual(len(tags), 3)

    def test_course_is_finished(self):
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)

        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        student = member.student

        course1.enroll(student)
        self.assertEqual(course1.is_finished(student), False)
        section1_1_1.pass_for_student(student)
        self.assertEqual(course1.is_finished(student), True)

    def test_course_professor_profile_picture(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        course1.enroll(member.student)
        client = Client()
        client.login(username='username', password='havijbastani1')
        response = client.get('/courses/' + course1.slug + '/chapters/')
        self.assertIsNot(None, response.context['professor'].get_profile_picture_url)
        self.assertIsNot(None, response.context['professor'].description)
        self.assertIsNot(None, response.context['professor'].member.username)

    def test_slug(self):
        slug = "my-slug"
        slug2 = "my-slug2"
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory(title="course title", slug=slug)
        self.assertEqual(course1.slug, slug)
        course1.slug = slug2
        course1.save()
        self.assertEqual(course1.slug, slug2)
        course2 = CourseFactory(title="title 1")
        self.assertEqual(course2.slug, "title-1")
        course2.title = "new title 1"
        course2.save()
        self.assertEqual(course2.title, "new title 1")
        self.assertEqual(course2.slug, "title-1")

    def test_recommendation(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        tag1 = RecommendationTagFactory()
        tag2 = RecommendationTagFactory()
        section1_1_1 = SectionFactory(chapter=chapter1_1, problem=ProblemFactory.create(course=course1))
        section1_1_1.recommendation_tags.set([tag1, tag2])
        c = Client()
        c.login(username='username', password='havijbastani1')
        response = c.get('/courses/recommendation/')
        courses = response.context['courses']
        self.assertEqual(len(courses), 1)
        course2 = CourseFactory()
        chapter2_1 = ChapterFactory(course=course2)
        section2_1_1 = SectionFactory(chapter=chapter2_1, problem=ProblemFactory.create(course=course2))
        section2_1_1.recommendation_tags.set([tag1, tag2])
        response = c.get('/courses/recommendation/')
        courses = response.context['courses']
        self.assertEqual(len(courses), 2)
        course1.enroll(member.student)
        c.get('/courses/{course_slug}/chapters/{chapter_slug}/sections/{section_slug}/pass'.
              format(course_slug=course1.slug, chapter_slug=chapter1_1.slug,
                     section_slug=section1_1_1.slug))
        response = c.get('/courses/recommendation/')
        courses = response.context['courses']
        self.assertEqual(len(courses), 1)
        course3 = CourseFactory(preconditions=(course2,))
        chapter3_1 = ChapterFactory(course=course3)
        section3_1_1 = SectionFactory(chapter=chapter3_1, problem=ProblemFactory.create(course=course2))
        response = c.get('/courses/recommendation/')
        courses = response.context['courses']
        self.assertEqual(len(courses), 1)

    def test_tagscore(self):
        member = MemberFactory(username='username', password='havijbastani1', is_student=True)
        tag0 = RecommendationTagFactory()
        tag1 = RecommendationTagFactory()
        tag2 = RecommendationTagFactory()
        tag3 = RecommendationTagFactory()
        course1 = CourseFactory()
        chapter1_1 = ChapterFactory(course=course1)
        section1_1_1 = SectionFactory(chapter=chapter1_1)
        section1_1_1.recommendation_tags.set([tag0, tag2, tag3])
        c = Client()
        c.login(username='username', password='havijbastani1')
        course1.enroll(member.student)
        section1_1_1.pass_for_student(member.student)
        self.assertEqual(TagScore.objects.get(tag=tag2, student=member.student).score, 1)
        course2 = CourseFactory()
        chapter2_1 = ChapterFactory(course=course2)
        section2_1_1 = SectionFactory(chapter=chapter2_1)
        section2_1_1.recommendation_tags.set([tag1, tag2])
        section2_1_2 = SectionFactory(chapter=chapter2_1)
        section2_1_2.recommendation_tags.set([tag1, tag3])
        course2.enroll(member.student)
        section2_1_1.pass_for_student(member.student)
        self.assertEqual(TagScore.objects.get(tag=tag2, student=member.student).score, 1)
        section2_1_2.pass_for_student(member.student)
        self.assertEqual(TagScore.objects.get(tag=tag0, student=member.student).score, 1)
        self.assertEqual(TagScore.objects.get(tag=tag1, student=member.student).score, 1)
        self.assertEqual(TagScore.objects.get(tag=tag2, student=member.student).score, 2)
        self.assertEqual(TagScore.objects.get(tag=tag3, student=member.student).score, 2)
