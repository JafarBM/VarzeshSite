from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse

from course import utils
from course.decorators import is_student_check, is_teacher_check
from .forms import FeedbackForm
from .models import Course, Section, Enrollment, Category, EnrollmentSectionPass, Feedback
from .models import SectionEnrollment
from .recommendation import get_recommendations


@login_required
@user_passes_test(test_func=is_student_check)
def recommendation(request):
    student = request.user.student
    courses = get_recommendations(student)

    context = dict()
    context['courses'] = [course for course in courses]
    context['categories'] = Category.objects.all()

    return render(
        request=request,
        template_name='course/course_list.html',
        context=context,
    )


@login_required
@user_passes_test(test_func=is_student_check)
def course_list(request):
    courses = Course.objects.prefetch_related('preconditions').all()
    category_id = request.GET.get('category_id', None)
    if category_id:
        courses = courses.filter(categories__in=[category_id])
    context = dict()
    context['courses'] = [course for course in courses]
    context['categories'] = Category.objects.all()

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
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('course', 'student', 'course__professor',
                                          'course__professor__member').prefetch_related('passed_sections'),
        student=student,
        course__slug=course_slug)
    chapters_progress = enrollment.get_chapter_passed_sections_progress()
    for key, value in chapters_progress.items():
        chapters_progress[key] = int(value)
    professor = enrollment.course.professor
    chapters_lock = {}

    for chapter in chapters_progress:
        chapters_lock[chapter] = chapter.is_lock(student, chapters_progress)

    context = {"chapters": utils.merge_dictionaries(progress=chapters_progress, is_locked=chapters_lock),
               "enrollment": enrollment,
               "professor": professor,
               "is_finished": enrollment.course.is_finished(student, chapters_progress=chapters_progress),
               }
    return render(
        request=request,
        template_name='course/chapter_list.html',
        context=context,
    )


@login_required
@user_passes_test(test_func=is_student_check)
def section_detail_view(request, course_slug, chapter_slug, section_slug):
    student = request.user.student
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('course', 'student'),
        student=student,
        course__slug=course_slug)
    section = get_object_or_404(Section.objects.select_related('chapter', 'chapter__course'),
                                chapter__course__slug=course_slug,
                                chapter__slug=chapter_slug, slug=section_slug)

    try:
        enrollment_section = SectionEnrollment.objects.get(student=student, section=section)
        enrollment_section.set_start_time()
    except SectionEnrollment.DoesNotExist:
        pass

    context = {'student': student, 'enrollment': enrollment, 'section': section,
               'next_section': section.get_next_section(), 'previous_section': section.get_previous_section(),
               'enrollment_section': enrollment_section, 'feedback_form': FeedbackForm()}
    return render(request, 'course/section-detail.html', context=context)


@login_required
@user_passes_test(test_func=is_student_check)
def section_unlock(request, course_slug, chapter_slug, section_slug):
    student = request.user.student
    student_credit = student.compute_credit()

    section = get_object_or_404(Section, chapter__course__slug=course_slug,
                                chapter__slug=chapter_slug, slug=section_slug)
    section_credit = section.credit
    enrollment = get_object_or_404(Enrollment, student=student, course__slug=course_slug)

    if enrollment.is_section_available(section) or enrollment.has_used_credit(section):
        return redirect(reverse('course:section-detail', args=[course_slug, chapter_slug, section_slug]))
    elif section_credit > student_credit:
        return render(
            request=request,
            template_name="course/insufficient_credit_course.html"
        )
    else:
        try:
            section.credit_logs.create(student=student, credit=-section_credit)
            enrollment.unlocked_sections.add(section)
            return redirect(reverse('course:section-detail', args=[course_slug, chapter_slug, section_slug]))
        except IntegrityError:
            return redirect(reverse('course:section-detail', args=[course_slug, chapter_slug, section_slug]))


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


@login_required
@user_passes_test(test_func=is_teacher_check)
def student_progress_list(request, course_slug):
    professor = request.user.professor
    try:
        course = Course.objects.get(slug=course_slug, professor=professor)
        context = {
            'course': course,
            'enrollments': Enrollment.objects.select_related('student').prefetch_related('passed_sections').filter(
                course=course)}
        return render(request, 'course/student-progress-list.html', context=context)
    except Course.DoesNotExist:
        return render(request,
                      "base.html",
                      context={"error": '!شما مدرس این درس نمی باشید'},
                      status=403)


@login_required
@user_passes_test(test_func=is_student_check)
def statistic_view(request, section_id):
    section = get_object_or_404(Section.objects.select_related('chapter', 'chapter__course'), id=section_id)
    return render(request, 'course/statistics_detail.html', context={"section": section})


def home(request):
    return render(request, 'base.html')
