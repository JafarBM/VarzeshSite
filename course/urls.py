from django.urls import path

from .views import course_list, section_detail_view, chapter_list, course_enroll, section_pass_view, \
    section_submit_feedback

app_name = 'course'

urlpatterns = [
    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>', section_detail_view,
         name='section-detail'),
    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>/pass', section_pass_view,
         name='section-pass'),
    path('<course_slug>/chapters/<chapter_slug>/sections/<section_slug>/submit_feedback', section_submit_feedback,
         name='section-submit-feedback'),
    path('<course_slug>/chapters/', chapter_list, name='chapter_list'),
    path('<course_slug>/enroll/', course_enroll, name='course_enroll'),
    path('', course_list, name='course_list'),
]
