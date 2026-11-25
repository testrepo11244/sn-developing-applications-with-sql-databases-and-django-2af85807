from django.contrib import admin

from .models import (
    Course,
    Lesson,
    Learner,
    Enrollment,
    Question,
    Choice,
    Submission,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ("choice_text", "is_correct")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("question_text", "grade", "course")
    show_change_link = True


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ("question_text", "course", "lesson", "grade")
    list_filter = ("course", "lesson")
    search_fields = ("question_text",)


class LessonAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "content")
    ordering = ("course", "order")


admin.site.site_header = "OnlineCourse Administration"
admin.site.site_title = "OnlineCourse Admin"
admin.site.index_title = "OnlineCourse Management"

admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Learner)
admin.site.register(Enrollment)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)