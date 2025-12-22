import uuid
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from users.models import User

class Language(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=50)
    flag_emoji = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'languages'
    
    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    total_lessons = models.IntegerField(default=0)
    total_exercises = models.IntegerField(default=0)
    
    is_free = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        db_table = 'courses'
    
    def __str__(self):
        return self.title

class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order_index = models.IntegerField()
    estimated_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    
    content_type = models.CharField(max_length=20, choices=[
        ('video', 'Video'),
        ('text', 'Text'),
        ('audio', 'Audio'),
        ('interactive', 'Interactive')
    ], default='text')
    
    content_url = models.URLField(blank=True, null=True)
    content_text = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    
    duration_minutes = models.IntegerField(default=15)
    difficulty_level = models.IntegerField(default=1)
    order_index = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    learning_objectives = models.JSONField(default=list, blank=True)
    key_vocabulary = models.JSONField(default=list, blank=True)
    grammar_points = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['order_index']
    
    def __str__(self):
        return self.title

class Exercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    
    exercise_type = models.CharField(max_length=30, choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('speaking', 'Speaking Practice'),
        ('listening', 'Listening Comprehension'),
        ('writing', 'Writing'),
        ('translation', 'Translation')
    ])
    
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    question_text = models.TextField(blank=True)
    question_audio_url = models.URLField(blank=True, null=True)
    question_image_url = models.URLField(blank=True, null=True)
    
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.TextField()
    acceptable_answers = models.JSONField(default=list, blank=True)
    
    points = models.IntegerField(default=10)
    time_limit_seconds = models.IntegerField(null=True, blank=True)
    max_attempts = models.IntegerField(default=3)
    
    hints = models.JSONField(default=list, blank=True)
    explanation = models.TextField(blank=True)
    
    order_index = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'exercises'
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"