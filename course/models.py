import datetime
from abc import abstractmethod

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.template.loader import get_template
from django.utils import timezone
from scipy import stats

from course.constants import DIFFICULTY_GROUPING_NUMBER, NAME_OF_DIFFICULTY_GROUPS, QUALITY_GROUPING_NUMBER, \
    NAME_OF_QUALITY_GROUPS, DEFAULT_YEAR_ADDITION, RATE_CHOICES
from course.constants import NULL_PROGRESS, FULL_PROGRESS, SLOW_COURSE_PROGRESS_LIMIT_DAYS, MAX_SECTION_RATE, \
    MIN_SECTION_RATE, DIGITS_AFTER_DECIMAL
from course.utils import is_same, workdays_between_count
from course.utils import split_time
from member.models import Professor, Student
from member.models import Professor, Student, CreditLog
from notification.tasks import send_mail


def default_base_course_start_time():
    current_time = timezone.now()
    default_time = current_time.replace(year=current_time.year + DEFAULT_YEAR_ADDITION)
    return default_time


class BaseCourse(models.Model):
    title = models.CharField(max_length=100)
    preconditions = models.ManyToManyField("self", blank=True, symmetrical=False)
    content = RichTextUploadingField(null=True)
    slug = models.SlugField(max_length=200, blank=True, null=True, unique=True)
    credit = models.IntegerField()
    credit_logs = GenericRelation(CreditLog)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug(self)
        super(BaseCourse, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @abstractmethod
    def is_lock(self, student):
        raise NotImplementedError

    @abstractmethod
    def is_finished(self, student):
        raise NotImplementedError

    @abstractmethod
    def logo_url(self):
        raise NotImplementedError

    @classmethod
    def generate_slug(cls, instance):
        slug = instance.title.replace(' ', '-')
        if cls.objects.filter(slug=slug):
            slug += '-{}'.format(instance.id)
        return slug


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RecommendationTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(BaseCourse):
    categories = models.ManyToManyField(Category, related_name='categories', blank=True)
    students = models.ManyToManyField(Student, through="Enrollment", related_name="courses")
    logo = models.ImageField(blank=True, upload_to='gallery-course')
    cover = models.ImageField(blank=True, upload_to='gallery-course')
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

    def get_sections_count(self):
        return Section.objects.filter(chapter__in=self.chapter_set.all()).count()

    def get_tags(self):
        sections = Section.objects.filter(chapter__course=self)
        tags = Tag.objects.filter(sections__in=sections).distinct()
        return tags

    def get_recommendation_tags(self):
        sections = Section.objects.filter(chapter__course=self)
        tags = RecommendationTag.objects.filter(sections__in=sections).distinct()
        return tags

    def is_lock(self, student, courses_progress=None):
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        if courses_progress is None:
            courses_progress = {}
            for enrollment in enrollments:
                courses_progress[enrollment.course] = enrollment.get_course_passed_sections_progress()
        preconditions = self.preconditions.all()
        for precondition in preconditions:
            if not is_same(courses_progress.get(precondition, NULL_PROGRESS), FULL_PROGRESS):
                return True
        return False

    def enroll(self, student):
        enrollment, is_created = Enrollment.objects.get_or_create(course=self, student=student)
        for section in Section.objects.filter(chapter__in=self.chapter_set.all()):
            SectionEnrollment.objects.get_or_create(student=student, section=section)
        return enrollment

    def is_finished(self, student, chapters_progress=None):
        try:
            enrollment = Enrollment.objects.get(course=self, student=student)
            if chapters_progress is None:
                chapters_progress = enrollment.get_chapter_passed_sections_progress()
            for chapter, progress in chapters_progress.items():
                if not is_same(progress, 100):
                    return False
            return True
        except Enrollment.DoesNotExist:
            return False

    def logo_url(self):
        if not self.logo:
            return settings.STATIC_URL + "images/default_logo.png"
        return self.logo.url

    def cover_url(self):
        if not self.cover:
            return settings.STATIC_URL + "images/default_cover.png"
        return self.cover.url

    def average_time_spent(self):
        enrollments = Enrollment.objects.filter(course=self).select_related('student')
        times_spent = []
        for enrollment in enrollments:
            if enrollment.end_date is not None:
                times_spent.append(enrollment.end_date - enrollment.start_date)
        if not len(times_spent):
            return 0
        return sum(times_spent, datetime.timedelta()) / len(times_spent)

    def get_student_rank_percentile(self, enrollment):
        return stats.percentileofscore(
            [enroll.get_course_passed_sections_progress() for enroll in Enrollment.objects.filter(course=self)],
            enrollment.get_course_passed_sections_progress())

    def get_course_progress(self, student):
        enrollment = Enrollment.objects.select_related('course').prefetch_related('passed_sections').filter(
            course=self,
            student=student)
        if enrollment:
            return enrollment[0].get_course_passed_sections_progress()
        return 0


class Chapter(BaseCourse):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order',)

    def is_lock(self, student, chapters_progress=None):
        preconditions = self.preconditions.all()
        if chapters_progress is None:
            enrollment = Enrollment.objects.get(student=student, course=self.course)
            chapters_progress = enrollment.get_chapter_passed_sections_progress()
        for precondition in preconditions:
            if not is_same(chapters_progress.get(precondition, NULL_PROGRESS), FULL_PROGRESS):
                return True
        return False

    def is_finished(self, student):
        try:
            sections = Section.objects.filter(chapter=self)
            passed_sections = Enrollment.objects.get(course=self.course, student=student).passed_sections.all()
            return True if all([section in passed_sections for section in sections]) else False
        except Enrollment.DoesNotExist:
            return False

    def logo_url(self):
        return self.course.logo_url()


class Section(BaseCourse):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections')
    tags = models.ManyToManyField(Tag, related_name='sections', blank=True)
    recommendation_tags = models.ManyToManyField(RecommendationTag, related_name='sections', blank=True)
    order = models.IntegerField()
    point = models.PositiveIntegerField()

    admin_rate = models.PositiveSmallIntegerField(
        choices=RATE_CHOICES,
        default=2
    )

    class Meta:
        ordering = ['order']
        unique_together = ('chapter', 'order',)

    def get_next_section(self):
        return self.chapter.sections.filter(order__gt=self.order).first()

    def get_previous_section(self):
        return self.chapter.sections.filter(order__lt=self.order).last()

    def is_lock(self, student):
        chapter = self.chapter
        course = chapter.course
        try:
            enrollment = Enrollment.objects.get(course=course, student=student)
            return enrollment.has_used_credit(self) and self.has_passed_preconditions(student)
        except Enrollment.DoesNotExist:
            return False

    def has_passed_preconditions(self, student):
        chapter = self.chapter
        course = chapter.course
        try:
            enrollment = Enrollment.objects.prefetch_related('passed_sections').get(course=course, student=student)
            passed_sections = enrollment.passed_sections.all()
            return not all([(precondition in passed_sections) for precondition in self.preconditions.all()])
        except Enrollment.DoesNotExist:
            return False

    def get_average_difficulty(self):
        query_set = Feedback.objects.filter(section=self)
        # when query_set be empty aggregate will return None
        # or 0 is for when query_set is empty
        average_difficulty = query_set.aggregate(Avg('difficulty'))['difficulty__avg'] or 0
        return round(average_difficulty, DIGITS_AFTER_DECIMAL)

    def get_average_quality(self):
        query_set = Feedback.objects.filter(section=self)
        average_quality = query_set.aggregate(Avg('quality'))['quality__avg'] or 0
        return round(average_quality, DIGITS_AFTER_DECIMAL)

    def get_feedbacks_count(self):
        return Feedback.objects.filter(section=self).count()

    def get_passer_count(self):
        return self.enrollments.count()

    def get_difficulty_grouping(self):
        feedbacks_count = self.get_feedbacks_count()
        if feedbacks_count == 0:
            return {}
        difficulty_grouping = {}
        group_interval_size = MAX_SECTION_RATE // DIFFICULTY_GROUPING_NUMBER
        first_of_interval = 1
        for i in range(DIFFICULTY_GROUPING_NUMBER - 1):
            difficulty_grouping[NAME_OF_DIFFICULTY_GROUPS[i]] = \
                Feedback.objects.filter(section=self,
                                        difficulty__gte=first_of_interval,
                                        difficulty__lt=first_of_interval + group_interval_size).count()
            first_of_interval += group_interval_size
        difficulty_grouping[
            NAME_OF_DIFFICULTY_GROUPS[DIFFICULTY_GROUPING_NUMBER - 1]] = \
            Feedback.objects.filter(section=self,
                                    difficulty__gte=first_of_interval,
                                    difficulty__lte=MAX_SECTION_RATE).count()
        for key, value in difficulty_grouping.items():
            difficulty_grouping[key] = value * 100 / feedbacks_count
        return difficulty_grouping

    def get_quality_grouping(self):
        feedbacks_count = self.get_feedbacks_count()
        if feedbacks_count == 0:
            return {}
        quality_grouping = {}
        group_interval_size = MAX_SECTION_RATE // QUALITY_GROUPING_NUMBER
        first_of_interval = 1
        for i in range(QUALITY_GROUPING_NUMBER - 1):
            quality_grouping[NAME_OF_QUALITY_GROUPS[i]] \
                = Feedback.objects.filter(section=self,
                                          quality__gte=first_of_interval,
                                          quality__lt=first_of_interval + group_interval_size).count()
            first_of_interval += group_interval_size

        quality_grouping[NAME_OF_QUALITY_GROUPS[QUALITY_GROUPING_NUMBER - 1]] \
            = Feedback.objects.filter(section=self,
                                      quality__gte=first_of_interval,
                                      quality__lte=MAX_SECTION_RATE).count()
        for key, value in quality_grouping.items():
            quality_grouping[key] = value * 100 / feedbacks_count
        return quality_grouping

    def pass_for_student(self, student):
        enrollment = Enrollment.objects.prefetch_related('passed_sections').select_related('course').get(
            course=self.chapter.course,
            student=student)
        if not enrollment:
            return False
        if not enrollment.is_section_available(self):
            return False
        if self.chapter.course.id == enrollment.course.id:
            if self not in enrollment.passed_sections.all():
                EnrollmentSectionPass.objects.create(enrollment=enrollment, section=self)
        if self.chapter.course.is_finished(student):
            enrollment.set_end()
        return True

    def is_finished(self, student, enrollment=None):
        try:
            if enrollment is None:
                enrollment = Enrollment.objects.get(course=self.chapter.course, student=student)
            EnrollmentSectionPass.objects.get(enrollment=enrollment, section=self)
            return True
        except EnrollmentSectionPass.DoesNotExist:
            return False

    def logo_url(self):
        return self.chapter.course.logo_url()

    def enroll(self, student):
        section_enrollment, is_created = SectionEnrollment.objects.get_or_create(section=self, student=student)
        return section_enrollment

    def get_splited_average_time_spent(self):
        average_time_spent = self.chapter.course.average_time_spent()
        return split_time(average_time_spent) if average_time_spent else 0


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    passed_sections = models.ManyToManyField(Section, blank=True, related_name='enrollments',
                                             through='EnrollmentSectionPass')
    unlocked_sections = models.ManyToManyField(Section, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ('course', 'student',)

    def __str__(self):
        return '{0} : {1}'.format(self.student, self.course)

    def is_section_available(self, section):
        enrollment_passed_sections = self.passed_sections.all()
        passed_preconditions = set(precondition for precondition in section.preconditions.all() if
                                   precondition not in enrollment_passed_sections)
        return len(passed_preconditions) == 0

    def has_used_credit(self, section):
        unlocked_sections = self.unlocked_sections.filter(pk=section.pk)
        return len(unlocked_sections) > 0

    def get_course_passed_sections_progress(self):
        passed_sections_number = self.passed_sections.all().count()
        course_sections_number = self.course.get_sections_count()
        if course_sections_number > 0:
            return (passed_sections_number / course_sections_number) * FULL_PROGRESS
        return NULL_PROGRESS

    def get_chapter_passed_sections_progress(self):
        passed_sections = self.passed_sections.all().select_related('chapter')
        chapters = Chapter.objects.prefetch_related('sections').filter(course=self.course)
        chapter_progress = {}
        for chapter in chapters:
            chapter_progress[chapter] = NULL_PROGRESS

        for passed_section in passed_sections:
            chapter_progress[passed_section.chapter] += 1

        for chapter in chapter_progress:
            sections_count = chapter.sections.count()
            if sections_count > 0:
                chapter_progress[chapter] /= sections_count
            else:
                chapter_progress[chapter] = NULL_PROGRESS
            chapter_progress[chapter] *= FULL_PROGRESS

        return chapter_progress

    def get_last_passed_section_datetime(self):
        return EnrollmentSectionPass.objects.filter(enrollment=self).order_by('end_date').last().end_date

    def is_progress_slow(self):
        last_passed_date = self.get_last_passed_section_datetime().date()
        return workdays_between_count(last_passed_date, timezone.now().date()) > SLOW_COURSE_PROGRESS_LIMIT_DAYS

    def check_and_send_slow_progress_email(self):
        if self.is_progress_slow():
            mail_subject = 'درس خود را پیگیری کنید !'

            message = get_template('course/course_slow_progress_email.html').render({
                'member': self.student.member,
                'course': self.course
            })
            to_email = self.student.member.email
            return send_mail(mail_subject, message, to_email)
        return False

    def get_elapsed_days_time_since_enroll(self):
        start = self.start_date
        until = self.end_date if self.end_date else timezone.now()

        return (until - start).days

    def set_end(self):
        self.end_date = timezone.now()
        self.save()

        tags = self.course.get_recommendation_tags()
        for tag in tags:
            tag_score, _ = TagScore.objects.get_or_create(tag=tag, student=self.student)
            tag_score.score += 1
            tag_score.save()


class EnrollmentSectionPass(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    end_date = models.DateTimeField(null=True, blank=True, default=timezone.now)

    def __str__(self):
        return "{} {}".format(self.enrollment, self.section)


class Feedback(models.Model):
    comment = models.TextField(verbose_name="نظر شما")
    difficulty = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(MAX_SECTION_RATE), MinValueValidator(MIN_SECTION_RATE)],
        default=1,
        verbose_name="سختی",
    )
    quality = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(MAX_SECTION_RATE), MinValueValidator(MIN_SECTION_RATE)],
        default=1,
        verbose_name="کیفیت",
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('section', 'student',)

    def __str__(self):
        return "comment: {comment}, difficulty: {difficulty}, quality: {quality}, student: {student}". \
            format(comment=self.comment,
                   difficulty=self.difficulty,
                   quality=self.quality,
                   student=self.student)


class SectionEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    started_time = models.DateTimeField(default=default_base_course_start_time)

    def set_start_time(self):
        current_time = timezone.now()
        if self.started_time > current_time:
            self.started_time = current_time
            self.save()

    def __str__(self):
        return "{} {}".format(self.student, self.section)


class TagScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tag = models.ForeignKey(RecommendationTag, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tag', 'student',)

    def __str__(self):
        return "{}: {}".format(self.student, self.tag)
