import factory
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from factory.django import DjangoModelFactory

from member.models import University, Major, Member, Student, Professor


class UniversityFactory(DjangoModelFactory):
    class Meta:
        model = University

    name = factory.sequence(lambda n: 'university{0}'.format(n))


class MajorFactory(DjangoModelFactory):
    class Meta:
        model = Major

    name = factory.sequence(lambda n: 'major{0}'.format(n))


@factory.django.mute_signals(post_save)
class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    university = factory.SubFactory(UniversityFactory)
    major = factory.SubFactory(MajorFactory)
    description = "lalalalalalalalalala"
    member = factory.SubFactory('course.tests.factories.MemberFactory', student=None)


@factory.django.mute_signals(post_save)
class ProfessorFactory(DjangoModelFactory):
    class Meta:
        model = Professor

    description = "lalalalalaalala"
    member = factory.SubFactory('course.tests.factories.MemberFactory', professor=None)


@factory.django.mute_signals(post_save)
class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    username = factory.sequence(lambda n: 'username{0}'.format(n))
    first_name = factory.sequence(lambda n: 'first_name{0}'.format(n))
    last_name = factory.sequence(lambda n: 'last_name{0}'.format(n))
    email = factory.lazy_attribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name))
    password = 'fatemejafardanial1'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['password'] = make_password(kwargs['password'])
        return super(MemberFactory, cls)._create(model_class, *args, **kwargs)

    student = factory.RelatedFactory(StudentFactory, 'member')
    professor = factory.RelatedFactory(ProfessorFactory, 'member')
