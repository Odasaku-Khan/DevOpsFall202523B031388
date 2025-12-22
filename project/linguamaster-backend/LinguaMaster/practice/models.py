import uuid
from django.db import models
from users.models import User
from courses.models import Course, Lesson, Exercise

class StudentEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    enrollment_status = models.CharField(max_length=20, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    current_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_time_minutes = models.IntegerField(default=0)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_enrollments'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title}"

class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['student', 'lesson']
    
    def __str__(self):
        return f"{self.student.email} - {self.lesson.title}"

class ExerciseAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_attempts')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='attempts')
    
    user_answer = models.TextField(blank=True)
    is_correct = models.BooleanField()
    score = models.IntegerField()
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    audio_url = models.URLField(blank=True, null=True)
    transcription = models.TextField(blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pronunciation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    whisper_analysis = models.JSONField(null=True, blank=True)
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exercise_attempts'
    
    def __str__(self):
        return f"{self.student.email} - {self.exercise.title}"