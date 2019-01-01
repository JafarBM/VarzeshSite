from django.urls import path

from .views import course_list, section_detail_view, chapter_list, course_enroll, \
    section_submit_feedback, student_progress_list, recommendation, section_unlock
from .views import statistic_view

app_name = 'course'

urlpatterns = [
    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>', section_detail_view,
         name='section-detail'),
    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>/submit_feedback', section_submit_feedback,
         name='section-submit-feedback'),
    path('<course_slug>/chapters/', chapter_list, name='chapter_list'),
    path('<course_slug>/enroll/', course_enroll, name='course_enroll'),

    path('<course_slug>/student_progress/', student_progress_list, name='student-progress-list'),
    path('', course_list, name='course_list'),
    path('section/statistic/<section_id>', statistic_view, name='statistic-view'),
    path('recommendation/', recommendation, name='recommendation'),

    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>/use-credit', section_unlock,
         name='section_unlock'),
]
