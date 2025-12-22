from django.db.models import Q
from courses.models import Course, Lesson, Exercise
from users.models import User

class SearchService:
    def search(self, query, filters=None, user=None):
        if not query or len(query.strip()) < 2:
            return {'results': [], 'total': 0}
        
        clean_query = self._clean_query(query)
        filters = filters or {}
        
        results = {
            'courses': self._search_courses(clean_query, filters, user),
            'lessons': self._search_lessons(clean_query, filters, user),
            'exercises': self._search_exercises(clean_query, filters, user),
            'users': self._search_users(clean_query, filters, user) if user else [],
        }
        
        combined = self._combine_results(results, clean_query)
        
        return {
            'query': query,
            'results': combined[:50],
            'total': len(combined),
            'by_type': {k: len(v) for k, v in results.items()}
        }
    
    def _search_courses(self, query, filters, user):
        qs = Course.objects.filter(is_active=True)
        
        if filters.get('language'):
            qs = qs.filter(language__code=filters['language'])
        
        if filters.get('level'):
            qs = qs.filter(level=filters['level'])
        
        results = qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-created_at')
        
        return [
            {
                'type': 'course',
                'id': str(course.id),
                'title': course.title,
                'description': course.description[:200] + '...' if course.description else '',
                'language': course.language.code,
                'level': course.level,
                'thumbnail': course.thumbnail_url,
                'relevance': 1.0
            }
            for course in results[:20]
        ]
    
    def _search_lessons(self, query, filters, user):
        qs = Lesson.objects.select_related('module', 'module__course').filter(
            is_active=True,
            module__course__is_active=True
        )
        
        if filters.get('course_id'):
            qs = qs.filter(module__course_id=filters['course_id'])
        
        results = qs.filter(
            Q(title__icontains=query) |
            Q(content_text__icontains=query)
        ).order_by('-created_at')
        
        return [
            {
                'type': 'lesson',
                'id': str(lesson.id),
                'title': lesson.title,
                'content_preview': lesson.content_text[:150] + '...' if lesson.content_text else '',
                'course_title': lesson.module.course.title,
                'course_id': str(lesson.module.course.id),
                'duration': lesson.duration_minutes,
                'relevance': 0.8
            }
            for lesson in results[:20]
        ]
    
    def _search_exercises(self, query, filters, user):
        qs = Exercise.objects.select_related('lesson', 'lesson__module', 'lesson__module__course').filter(
            is_active=True,
            lesson__is_active=True,
            lesson__module__course__is_active=True
        )
        
        if filters.get('exercise_type'):
            qs = qs.filter(exercise_type=filters['exercise_type'])
        
        results = qs.filter(
            Q(title__icontains=query) |
            Q(question_text__icontains=query)
        ).order_by('-created_at')
        
        return [
            {
                'type': 'exercise',
                'subtype': exercise.exercise_type,
                'id': str(exercise.id),
                'title': exercise.title,
                'question_preview': exercise.question_text[:100] + '...' if exercise.question_text else '',
                'lesson_title': exercise.lesson.title,
                'course_title': exercise.lesson.module.course.title,
                'points': exercise.points,
                'relevance': 0.6
            }
            for exercise in results[:20]
        ]
    
    def _search_users(self, query, filters, user):
        qs = User.objects.filter(is_active=True)
        
        if filters.get('user_type'):
            qs = qs.filter(user_type=filters['user_type'])
        
        results = qs.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).order_by('-date_joined')
        
        return [
            {
                'type': 'user',
                'id': str(user.id),
                'name': user.get_full_name() or user.username,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'avatar': user.avatar_url,
                'relevance': 0.9
            }
            for user in results[:10]
        ]
    
    def _clean_query(self, query):
        import re
        query = ' '.join(query.split())
        query = re.sub(r'[^\w\s\-]', '', query)
        return query.strip().lower()
    
    def _combine_results(self, results, query):
        combined = []
        
        for entity_type, entity_results in results.items():
            for result in entity_results:
                type_weights = {
                    'course': 1.2,
                    'lesson': 1.0,
                    'exercise': 0.8,
                    'user': 1.1
                }
                
                result['final_score'] = result.get('relevance', 0) * type_weights.get(entity_type, 1.0)
                combined.append(result)
        
        combined.sort(key=lambda x: x['final_score'], reverse=True)
        return combined