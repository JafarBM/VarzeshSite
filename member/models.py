from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django_jalali.db import models as jmodels

from course.constants import NO_PROFILE_IMAGE_URL, MEMBER_UPLOAD_PICTURES


class University(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="نام دانشگاه",
    )

    def __str__(self):
        return self.name


class Major(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="رشته‌ی تحصیلی",
    )

    def __str__(self):
        return self.name


class Member(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Professor(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, primary_key=True, related_name='professor')
    profile_picture = models.ImageField(upload_to=MEMBER_UPLOAD_PICTURES,
                                        blank=True)
    description = models.TextField()

    def __str__(self):
        return self.member.__str__()

    def get_profile_picture_url(self):
        try:
            return self.profile_picture.url
        except ValueError:
            return settings.STATIC_URL + NO_PROFILE_IMAGE_URL


class Student(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, primary_key=True, related_name='student')
    profile_picture = models.ImageField(upload_to=MEMBER_UPLOAD_PICTURES,
                                        blank=True)
    description = models.TextField()
    university = models.ForeignKey(
        University,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="نام دانشگاه",
    )

    major = models.ForeignKey(
        Major,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="رشته‌ی تحصیلی",
    )

    def __str__(self):
        return self.member.__str__()

    def get_profile_picture_url(self):
        try:
            return self.profile_picture.url
        except ValueError:
            return settings.STATIC_URL + NO_PROFILE_IMAGE_URL

    def compute_credit(self):
        res = CreditLog.objects.defer("content_object", "content_type", "object_id").filter(
            student=self).aggregate(Sum('credit'))['credit__sum']
        if res is None:
            return 0
        return res


class CreditLog(models.Model):
    student = models.ForeignKey(Student, db_index=True, on_delete=models.CASCADE)
    credit = models.IntegerField()
    date = jmodels.jDateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        unique_together = ('student', 'content_type', 'object_id')
