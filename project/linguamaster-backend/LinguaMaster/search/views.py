
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import SearchService

class SearchView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query', '').strip()
        filters = request.data.get('filters', {})
        
        if len(query) < 2:
            return Response({
                'success': True,
                'results': [],
                'total': 0
            })
        
        search_service = SearchService()
        results = search_service.search(query, filters, request.user)
        
        return Response({
            'success': True,
            'data': results
        })