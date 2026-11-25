from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Learner(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    occupation = models.CharField(max_length=100, blank=True)
    social_link = models.URLField(blank=True)

    def __str__(self):
        return self.user.get_username()


class Enrollment(models.Model):
    MODE_CHOICES = [
        ("audit", "Audit"),
        ("honor", "Honor"),
        ("verified", "Verified"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="audit")
    rating = models.FloatField(default=5.0)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-date_enrolled"]

    def __str__(self):
        return f"{self.user.get_username()} enrolled in {self.course.name}"


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
    )
    question_text = models.CharField(max_length=200)
    grade = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_submitted"]

    def __str__(self):
        return f"Submission {self.pk} by {self.enrollment.user.get_username()}"