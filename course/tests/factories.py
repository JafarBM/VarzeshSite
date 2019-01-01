import datetime

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from course.models import Course, Category, Tag, Chapter, Section, Enrollment, BaseCourse, Feedback, RecommendationTag
from course.models import EnrollmentSectionPass
from member.models import CreditLog
from member.tests.factories import CreditLogFactory
from member.tests.factories import MemberFactory, ProfessorFactory, StudentFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.sequence(lambda n: 'category{0}'.format(n))


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.sequence(lambda n: 'tag{0}'.format(n))


class RecommendationTagFactory(DjangoModelFactory):
    class Meta:
        model = RecommendationTag

    name = factory.sequence(lambda n: 'recom-tag{0}'.format(n))


class BaseCourseFactory(DjangoModelFactory):
    class Meta:
        model = BaseCourse

    title = factory.sequence(lambda n: 'title{0}'.format(n))
    credit = 100

    @factory.post_generation
    def preconditions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for precondition in extracted:
                self.preconditions.add(precondition)


class CourseFactory(BaseCourseFactory):
    class Meta:
        model = Course

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category in extracted:
                self.categories.add(category)

    professor = factory.SubFactory(ProfessorFactory)


class ChapterFactory(BaseCourseFactory):
    class Meta:
        model = Chapter

    course = factory.SubFactory(CourseFactory)
    order = factory.sequence(lambda n: n)


class SectionFactory(BaseCourseFactory):
    class Meta:
        model = Section

    problem = factory.SubFactory('exercise.tests.factories.ProblemFactory')
    chapter = factory.SubFactory(ChapterFactory)
    order = factory.sequence(lambda n: n)
    point = factory.sequence(lambda n: n)
    admin_rate = factory.sequence(lambda n: (n % 10) + 1)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = Enrollment

    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(StudentFactory)
    start_date = datetime.date.today()
    end_date = None

    @factory.post_generation
    def passed_sections(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for passed_section in extracted:
                self.passed_sections.add(passed_section)

    @factory.post_generation
    def unlocked_sections(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for unlocked_section in extracted:
                self.unlocked_sections.add(unlocked_section)


class EnrollmentSectionPassFactory(DjangoModelFactory):
    class Meta:
        model = EnrollmentSectionPass

    enrollment = factory.SubFactory(EnrollmentFactory)
    section = factory.SubFactory(SectionFactory)
    end_date = timezone.now()


class MemberWithCourseFactory(MemberFactory):
    enrollment = factory.RelatedFactory(EnrollmentFactory, 'member')


class MemberWith2CoursesFactory(MemberFactory):
    enrollment1 = factory.RelatedFactory(EnrollmentFactory, 'member', course__name='Course1')
    enrollment2 = factory.RelatedFactory(EnrollmentFactory, 'member', course__name='Course2')


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    comment = factory.sequence(lambda n: 'comment{0}'.format(n))
    section = factory.SubFactory(SectionFactory)
    student = factory.SubFactory(StudentFactory)
    difficulty = factory.sequence(lambda n: (n % 10) + 1)
    quality = factory.sequence(lambda n: (n % 10) + 1)


class CourseLogFactory(CreditLogFactory):
    content_object = factory.SubFactory(CourseFactory)

    class Meta:
        model = CreditLog


class ChapterLogFactory(CreditLogFactory):
    content_object = factory.SubFactory(ChapterFactory)

    class Meta:
        model = CreditLog


class SectionLogFactory(CreditLogFactory):
    content_object = factory.SubFactory(SectionFactory)

    class Meta:
        model = CreditLog
