from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from .models import Language, Course, Module, Lesson, Exercise
from .serializers import (LanguageSerializer, CourseSerializer,
                         ModuleSerializer, LessonSerializer, ExerciseSerializer)

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        language = self.request.query_params.get('language')
        level = self.request.query_params.get('level')
        search = self.request.query_params.get('search')
        
        queryset = Course.objects.filter(is_active=True)
        
        if language:
            queryset = queryset.filter(language__code=language)
        
        if level:
            queryset = queryset.filter(level=level)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def modules(self, request, pk=None):
        course = self.get_object()
        modules = course.modules.filter(is_active=True).order_by('order_index')
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)

class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(
                course_id=course_id,
                is_active=True
            ).order_by('order_index')
        return Module.objects.none()
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        module = self.get_object()
        lessons = module.lessons.filter(is_active=True).order_by('order_index')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if module_id:
            return Lesson.objects.filter(
                module_id=module_id,
                is_active=True
            ).order_by('order_index')
        return Lesson.objects.none()
    
    @action(detail=True, methods=['get'])
    def exercises(self, request, pk=None):
        lesson = self.get_object()
        exercises = lesson.exercises.filter(is_active=True).order_by('order_index')
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        score = request.data.get('score', 0)
        time_spent = request.data.get('time_spent', 0)
        
        from practice.models import LessonProgress
        progress, created = LessonProgress.objects.update_or_create(
            student=request.user,
            lesson=lesson,
            defaults={
                'is_completed': True,
                'score': score,
                'time_spent_minutes': time_spent,
            }
        )
        
        return Response({'success': True, 'progress_id': str(progress.id)})

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            return Exercise.objects.filter(
                lesson_id=lesson_id,
                is_active=True
            ).order_by('order_index')
        return Exercise.objects.none()
    
    @action(detail=True, methods=['post'])
    def attempt(self, request, pk=None):
        exercise = self.get_object()
        user_answer = request.data.get('answer')
        
        from practice.models import ExerciseAttempt
        attempt = ExerciseAttempt.objects.create(
            student=request.user,
            exercise=exercise,
            user_answer=user_answer,
            is_correct=user_answer == exercise.correct_answer,
            score=exercise.points if user_answer == exercise.correct_answer else 0
        )
        
        return Response({
            'success': True,
            'attempt_id': str(attempt.id),
            'is_correct': attempt.is_correct,
            'score': attempt.score,
            'explanation': exercise.explanation
        })