import datetime

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from course.models import Course, Category, Tag, Chapter, Section, Enrollment, BaseCourse, Feedback
from course.models import EnrollmentSectionPass
from member.tests.factories import MemberFactory, ProfessorFactory, StudentFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.sequence(lambda n: 'category{0}'.format(n))


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.sequence(lambda n: 'tag{0}'.format(n))


class BaseCourseFactory(DjangoModelFactory):
    class Meta:
        model = BaseCourse

    title = factory.sequence(lambda n: 'title{0}'.format(n))

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
    member = factory.SubFactory(MemberFactory)
    start_date = datetime.date.today()
    end_date = datetime.date.today()

    @factory.post_generation
    def passed_sections(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for passed_section in extracted:
                self.passed_sections.add(passed_section)


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
