from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from course import utils
from course.constants import MAX_SECTION_RATE
from course.utils import is_student_check, add_navbar_data_context
from notification.utils import new_notification_check
from .forms import FeedbackForm
from .models import Course, Section, Enrollment, Category, EnrollmentSectionPass, Feedback
from .models import SectionEnrollment


@login_required
@user_passes_test(test_func=is_student_check)
def course_list(request):
    courses = Course.objects.all()
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student)

    category_id = request.GET.get('category_id', None)

    if category_id:
        courses = Course.objects.filter(categories__in=[category_id])
        enrollments = enrollments.filter(course__categories__in=[category_id])

    courses_progress = {}
    courses_lock = {}
    can_enroll = {}
    tags = {}
    covers = {}

    for course in courses:
        courses_progress[course] = 0
        can_enroll[course] = True
        courses_lock[course] = course.is_lock(student)
        tags[course] = course.get_tags()
        covers[course] = course.cover_url()

    for enrollment in enrollments:
        courses_progress[enrollment.course] = enrollment.get_course_passed_sections_progress()
        can_enroll[enrollment.course] = False

    context = {"courses": utils.merge_dictionaries(
        progress=courses_progress, is_locked=courses_lock, can_enroll=can_enroll, tags=tags),
        "categories": Category.objects.all(),
    }
    context = add_navbar_data_context(student_username=request.user.username,
                                      notification_count=new_notification_check(student),
                                      student=student,
                                      context=context)

    return render(
        request=request,
        template_name='course/course_list.html',
        context=context,
    )


@login_required
@user_passes_test(test_func=is_student_check)
def course_enroll(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    student = request.user.student
    course.enroll(student)
    return redirect(reverse('course:chapter_list', args=[course_slug]))


@login_required
@user_passes_test(test_func=is_student_check)
def chapter_list(request, course_slug):
    student = request.user.student
    enrollment = get_object_or_404(Enrollment, student=student, course__slug=course_slug)
    chapters_progress = enrollment.get_chapter_passed_sections_progress()
    chapters_lock = {}

    for chapter in chapters_progress:
        chapters_lock[chapter] = chapter.is_lock(student)

    context = {"chapters": utils.merge_dictionaries(progress=chapters_progress, is_locked=chapters_lock),
               "started_date": enrollment.start_date,
               "is_finished": enrollment.course.is_finished(student),
               "professor_description": enrollment.course.professor.description,
               "professor_picture_url": enrollment.course.professor.get_profile_picture_url(),
               "professor_name": enrollment.course.professor.member.username,
               "current_course_link": "/courses/" + course_slug + "/chapters/",
               "course": enrollment.course,
               }
    context = add_navbar_data_context(student_username=request.user.username,
                                      notification_count=new_notification_check(student),
                                      student=student,
                                      context=context)
    return render(
        request=request,
        template_name='course/chapter_list.html',
        context=context,
    )


@login_required
@user_passes_test(test_func=is_student_check)
def section_detail_view(request, course_slug, chapter_slug, section_slug):
    student = request.user.student
    enrollment = get_object_or_404(Enrollment, student=student, course__slug=course_slug)
    section = get_object_or_404(Section, chapter__course__slug=course_slug,
                                chapter__slug=chapter_slug, slug=section_slug)

    data = {'current': section,
            'next': section.get_next_section(),
            'previous': section.get_previous_section()}

    context = {}
    for k, v in data.items():
        context[k] = {'section': v, 'is_available': False if v is None else enrollment.is_section_available(v),
                      'is_passed': False if v is None else enrollment.passed_sections.filter(slug=v.slug).count() > 0,
                      }

    try:
        enrollment_section = SectionEnrollment.objects.get(student=student, section=section)
        current_time = timezone.now()
        if enrollment_section.started_time > current_time:
            enrollment_section.started_time = current_time
            enrollment_section.save()
        context['started_time'] = enrollment_section.started_time
    except SectionEnrollment.DoesNotExist:
        pass
    context['is_finished'] = section.is_finished(student=student)
    context['orange_star_number'] = section.admin_rate
    context['black_star_number'] = MAX_SECTION_RATE - section.admin_rate
    context['max_section_rate'] = MAX_SECTION_RATE

    context['feedback_form'] = FeedbackForm()

    context['average_difficulty'] = section.get_average_difficulty()
    context['average_quality'] = section.get_average_quality()
    context['passer_count'] = section.get_passer_count()
    feedbacks_count = section.get_feedbacks_count()
    context['feedback_count'] = feedbacks_count
    # TODO average_time_spent, starter_cnt
    context['average_time_spent'] = 0
    difficulty_grouping = section.get_difficulty_grouping()
    quality_grouping = section.get_quality_grouping()

    context['difficulty_grouping'] = 0
    context['quality_grouping'] = 0

    context["current_course_link"] = "/courses/" + course_slug + "/chapters/"
    context = add_navbar_data_context(student_username=request.user.username,
                                      notification_count=new_notification_check(student),
                                      student=student,
                                      context=context)

    if feedbacks_count != 0:
        context['difficulty_grouping'] = {k: 100.0 * v / feedbacks_count for k, v in difficulty_grouping.items()}
        context['quality_grouping'] = {k: 100.0 * v / feedbacks_count for k, v in quality_grouping.items()}

    return render(request, 'course/section-detail.html', context=context)


@login_required
@user_passes_test(test_func=is_student_check)
def section_pass_view(request, course_slug, chapter_slug, section_slug):
    student = request.user.student
    enrollment = get_object_or_404(Enrollment, student=student, course__slug=course_slug)
    section = get_object_or_404(Section, chapter__course__slug=course_slug,
                                chapter__slug=chapter_slug, slug=section_slug)

    data = {'passed': False}
    if enrollment.is_section_available(section):
        section.pass_for_student(student)
        data['passed'] = True

    return JsonResponse(data)


@login_required
@user_passes_test(test_func=is_student_check)
def section_submit_feedback(request, course_slug, chapter_slug, section_slug):
    student = request.user.student
    enrollment = get_object_or_404(Enrollment, student=student, course__slug=course_slug)
    section = get_object_or_404(Section, chapter__course__slug=course_slug,
                                chapter__slug=chapter_slug, slug=section_slug)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            if EnrollmentSectionPass.objects.filter(enrollment=enrollment, section=section).count() > 0:
                Feedback.objects.get_or_create(section=section, student=student, comment=form.cleaned_data['comment'],
                                               difficulty=int(form.cleaned_data['difficulty']),
                                               quality=int(form.cleaned_data['quality']))

                next_section = section.get_next_section()
                if next_section:
                    return redirect(reverse('course:section-detail',
                                            args=[course_slug, chapter_slug, next_section.slug]))
                else:
                    return redirect(reverse('course:chapter_list', args=[course_slug]))

    return redirect(reverse('course:section-detail', args=[course_slug, chapter_slug, section_slug]))
