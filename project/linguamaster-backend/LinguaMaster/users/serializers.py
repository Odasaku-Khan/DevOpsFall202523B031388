from rest_framework import serializers
from .models import User, UserPreferences

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                 'user_type', 'target_language', 'learning_languages',
                 'streak_days', 'total_xp', 'avatar_url', 'date_joined',
                 'last_login']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name',
                 'last_name', 'target_language']
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Minimum 8 characters")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Must contain uppercase")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Must contain lowercase")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Must contain number")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            target_language=validated_data.get('target_language', 'fr')
        )
        UserPreferences.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    preferences = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                 'user_type', 'target_language', 'learning_languages',
                 'daily_goal_minutes', 'streak_days', 'total_xp',
                 'bio', 'avatar_url', 'phone_number', 'country',
                 'timezones', 'language_preference', 'preferences']
    
    def get_preferences(self, obj):
        try:
            pref = obj.preferences
            return {
                'email_notifications': pref.email_notifications,
                'push_notifications': pref.push_notifications,
                'auto_play_audio': pref.auto_play_audio,
                'show_translations': pref.show_translations,
                'show_on_leaderboard': pref.show_on_leaderboard,
                'allow_social_features': pref.allow_social_features,
            }
        except UserPreferences.DoesNotExist:
            return {}