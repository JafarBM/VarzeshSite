from course.constants import NUMBER_OF_RECOMMEND, MINIMUM_SCORE_FOR_RECOMMEND
from .models import TagScore, Course, Enrollment


def get_recommendations(student):
    tags = TagScore.objects.filter(student=student)
    tag_scores = {i.tag: i.score for i in tags}
    course_scores = []
    all_course = Course.objects.all()
    for course in all_course:
        if (not course.is_lock(student)) and (not Enrollment.objects.filter(student=student, course=course).exists()):
            score = 0
            course_tags = course.get_tags()
            for tag in course_tags:
                if tag in tag_scores:
                    score += tag_scores[tag]
            course_scores.append((score, course))
    course_scores.sort(key=lambda course_score: (course_score[0], course_score[1].id), reverse=True)
    recommends = []
    for counter in range(0, min(NUMBER_OF_RECOMMEND, len(course_scores))):
        if course_scores[counter][0] >= MINIMUM_SCORE_FOR_RECOMMEND:
            recommends.append(course_scores[counter][1])
    return recommends
