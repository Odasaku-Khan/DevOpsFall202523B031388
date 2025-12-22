from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import json

from .models import StudentEnrollment, LessonProgress, ExerciseAttempt
from .services import SpeechRecognitionService
from courses.models import Exercise

class StudentEnrollmentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=request.user,
            course_id=course_id,
            defaults={'enrollment_status': 'active'}
        )
        
        return Response({
            'success': True,
            'enrollment_id': str(enrollment.id),
            'created': created
        })

class SpeakingPracticeView(views.APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        audio_file = request.FILES.get('audio')
        exercise_id = request.data.get('exercise_id')
        reference_text = request.data.get('reference_text')
        language = request.data.get('language', 'fr')
        
        if not audio_file or not exercise_id:
            return Response({'error': 'audio and exercise_id required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        filename = f"speaking_practice/{uuid.uuid4()}_{audio_file.name}"
        saved_path = default_storage.save(filename, ContentFile(audio_file.read()))
        
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            speech_service = SpeechRecognitionService()
            
            temp_file_path = default_storage.path(saved_path)
            analysis_result = speech_service.analyze_pronunciation(
                temp_file_path,
                reference_text or exercise.correct_answer,
                language
            )
            
            if not analysis_result['success']:
                return Response({'error': analysis_result.get('error')}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            attempt = ExerciseAttempt.objects.create(
                student=request.user,
                exercise=exercise,
                user_answer=analysis_result['transcription'],
                audio_url=saved_path,
                transcription=analysis_result['transcription'],
                confidence_score=analysis_result.get('confidence', 0),
                pronunciation_score=analysis_result['score'],
                feedback=json.dumps(analysis_result['feedback']),
                whisper_analysis=json.dumps(analysis_result),
                is_correct=analysis_result['score'] >= 70,
                score=int(analysis_result['score'])
            )
            
            return Response({
                'success': True,
                'attempt_id': str(attempt.id),
                'analysis': {
                    'transcription': analysis_result['transcription'],
                    'confidence': analysis_result.get('confidence', 0),
                    'accuracy': analysis_result['accuracy'],
                    'score': analysis_result['score'],
                    'feedback': analysis_result['feedback']
                }
            })
            
        except Exception as e:
            default_storage.delete(saved_path)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        enrollments = StudentEnrollment.objects.filter(
            student=request.user,
            enrollment_status='active'
        ).select_related('course')
        
        lesson_progress = LessonProgress.objects.filter(
            student=request.user,
            is_completed=True
        ).count()
        
        exercise_attempts = ExerciseAttempt.objects.filter(
            student=request.user
        ).count()
        
        total_time = StudentEnrollment.objects.filter(
            student=request.user
        ).aggregate(total=models.Sum('total_time_minutes'))['total'] or 0
        
        return Response({
            'enrollments': [{
                'course_id': str(e.course.id),
                'course_title': e.course.title,
                'progress': float(e.progress_percentage),
                'total_time': e.total_time_minutes,
                'status': e.enrollment_status
            } for e in enrollments],
            'stats': {
                'lessons_completed': lesson_progress,
                'exercises_attempted': exercise_attempts,
                'total_time_minutes': total_time,
                'current_streak': request.user.streak_days,
                'total_xp': request.user.total_xp
            }
        })