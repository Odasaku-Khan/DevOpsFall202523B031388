from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Sum, Avg
from practice.models import LessonProgress, ExerciseAttempt
from practice.models import StudentEnrollment

class AnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        lessons_completed = LessonProgress.objects.filter(
            student=user,
            is_completed=True
        ).count()
        
        exercises_completed = ExerciseAttempt.objects.filter(
            student=user
        ).count()
        
        total_time = StudentEnrollment.objects.filter(
            student=user
        ).aggregate(total=Sum('total_time_minutes'))['total'] or 0
        
        speaking_practices = ExerciseAttempt.objects.filter(
            student=user,
            exercise__exercise_type='speaking'
        ).count()
        
        avg_score = ExerciseAttempt.objects.filter(
            student=user
        ).aggregate(avg=Avg('score'))['avg'] or 0
        
        enrollments = StudentEnrollment.objects.filter(
            student=user
        ).count()
        
        return Response({
            'user_id': str(user.id),
            'stats': {
                'lessons_completed': lessons_completed,
                'exercises_completed': exercises_completed,
                'speaking_practices': speaking_practices,
                'total_time_minutes': total_time,
                'average_score': round(avg_score, 1),
                'current_streak': user.streak_days,
                'total_xp': user.total_xp,
                'enrollments': enrollments
            },
            'daily_goal': {
                'target': user.daily_goal_minutes,
                'achieved': total_time >= user.daily_goal_minutes
            }
        })