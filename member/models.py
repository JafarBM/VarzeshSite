from django.contrib.auth.models import AbstractUser
from django.db import models

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
            return NO_PROFILE_IMAGE_URL


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
            return NO_PROFILE_IMAGE_URL
