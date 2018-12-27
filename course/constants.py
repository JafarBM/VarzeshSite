from django.conf import settings

FULL_PROGRESS = 100
NULL_PROGRESS = 0

SLOW_COURSE_PROGRESS_LIMIT_DAYS = 2
SLOW_COURSE_PROGRESS_JOB_RUNTIME = {'hour': 23, 'minute': 0}

WEEKENDS = [3, 4]

MIN_SECTION_RATE = 1
MAX_SECTION_RATE = 3  # FIXED please-don't-edit

DEFAULT_YEAR_ADDITION = 2000
DIFFICULTY_GROUPING_NUMBER = 3
NAME_OF_DIFFICULTY_GROUPS = ['آسان', 'متوسط', 'سخت']

QUALITY_GROUPING_NUMBER = 3
NAME_OF_QUALITY_GROUPS = ['بد', 'متوسط', 'خوب']

RATE_CHOICES = [
    (1, 'آسان'),
    (2, 'متوسط'),
    (3, 'سخت')
]
NO_PROFILE_IMAGE_URL = settings.STATIC_URL + 'images/1024px-No_image_available.svg.png'
MEMBER_UPLOAD_PICTURES = "member_gallery/"
