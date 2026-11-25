from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .models import Choice, Course, Enrollment, Question, Submission


class CourseListView(ListView):
    model = Course
    template_name = "onlinecourse/index_bootstrap.html"
    context_object_name = "course_list"
    ordering = ["name"]


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method == "POST":
        selected_choices = []

        for key in request.POST:
            if not key.startswith("choice_"):
                continue

            for choice_id in request.POST.getlist(key):
                try:
                    choice = Choice.objects.get(
                        pk=choice_id,
                        question__course=course,
                    )
                except (Choice.DoesNotExist, ValueError):
                    continue

                if choice not in selected_choices:
                    selected_choices.append(choice)

        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_choices)

        return redirect(
            "onlinecourse:show_exam_result",
            course_id=course.id,
            submission_id=submission.id,
        )

    questions = Question.objects.filter(course=course).prefetch_related("choice_set")
    return render(
        request,
        "onlinecourse/exam.html",
        {
            "course": course,
            "questions": questions,
            "enrollment": enrollment,
        },
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course,
    )

    selected_choice_ids = set(
        submission.choices.values_list("id", flat=True)
    )
    questions = Question.objects.filter(course=course).prefetch_related("choice_set")

    total_score = 0
    max_score = 0
    results = []

    for question in questions:
        max_score += question.grade
        correct_ids = set(
            question.choice_set.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_ids = set(
            question.choice_set.filter(id__in=selected_choice_ids).values_list(
                "id", flat=True
            )
        )
        is_correct = bool(correct_ids) and selected_ids == correct_ids

        if is_correct:
            total_score += question.grade

        results.append(
            {
                "question": question,
                "selected_choices": question.choice_set.filter(id__in=selected_ids),
                "correct_choices": question.choice_set.filter(id__in=correct_ids),
                "is_correct": is_correct,
            }
        )

    percentage = (total_score / max_score * 100) if max_score else 0
    passed = percentage >= 70

    context = {
        "course": course,
        "submission": submission,
        "results": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": round(percentage, 1),
        "passed": passed,
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)