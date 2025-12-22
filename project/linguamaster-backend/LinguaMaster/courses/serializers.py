from rest_framework import serializers
from .models import Language, Course, Module, Lesson, Exercise

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name', 'native_name', 'flag_emoji']

class CourseSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    language_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'language', 'language_id', 'title', 'description',
                 'thumbnail_url', 'level', 'estimated_hours', 'total_lessons',
                 'total_exercises', 'is_free', 'is_featured', 'is_active',
                 'created_at']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order_index',
                 'estimated_minutes', 'is_active']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'content_type', 'content_url',
                 'content_text', 'thumbnail_url', 'duration_minutes',
                 'difficulty_level', 'order_index', 'is_active',
                 'learning_objectives', 'key_vocabulary', 'grammar_points',
                 'created_at']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'lesson', 'exercise_type', 'title', 'instructions',
                 'question_text', 'question_audio_url', 'question_image_url',
                 'options', 'correct_answer', 'acceptable_answers',
                 'points', 'time_limit_seconds', 'max_attempts',
                 'hints', 'explanation', 'order_index', 'is_active']