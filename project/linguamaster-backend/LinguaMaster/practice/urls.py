from django.urls import path
from . import views

urlpatterns = [
    path('enroll/', views.StudentEnrollmentView.as_view(), name='enroll'),
    path('speaking/', views.SpeakingPracticeView.as_view(), name='speaking_practice'),
    path('progress/', views.ProgressView.as_view(), name='progress'),
]