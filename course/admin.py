from django.contrib import admin

from course.models import TagScore, RecommendationTag
from .models import Course, Chapter, Section, Category, Tag, Enrollment, EnrollmentSectionPass, Feedback
from .models import SectionEnrollment


class SectionInline(admin.TabularInline):
    model = Section
    exclude = ['preconditions']
    extra = 0


class ChapterAdmin(admin.ModelAdmin):
    model = Chapter
    inlines = [
        SectionInline,
    ]


class ChapterInline(admin.TabularInline):
    model = Chapter
    exclude = ['preconditions']
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    model = Course
    inlines = [ChapterInline, ]
    filter_horizontal = ['preconditions', 'categories']


admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Enrollment)
admin.site.register(Feedback)
admin.site.register(EnrollmentSectionPass)
admin.site.register(SectionEnrollment)
admin.site.register(TagScore)
admin.site.register(RecommendationTag)
