import uuid
from django.db import models
from users.models import User

class UserAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(auto_now_add=True)
    
    lessons_completed = models.IntegerField(default=0)
    exercises_completed = models.IntegerField(default=0)
    speaking_practices = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    streak_maintained = models.BooleanField(default=False)
    
    daily_goal_achieved = models.BooleanField(default=False)
    weekly_goal_achieved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_analytics'
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"

class Achievement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    
    achievement_type = models.CharField(max_length=30, choices=[
        ('streak', 'Streak'),
        ('completion', 'Completion'),
        ('speed', 'Speed'),
        ('accuracy', 'Accuracy'),
        ('social', 'Social'),
        ('special', 'Special')
    ])
    
    requirement_type = models.CharField(max_length=30)
    requirement_value = models.IntegerField()
    xp_reward = models.IntegerField(default=100)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'achievements'
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"