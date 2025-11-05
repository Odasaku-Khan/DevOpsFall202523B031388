from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=False, null=False)
    birthday = models.DateField(blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='authentification_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='authetification_permission_set',
        blank=True,
        help_text='Specific permission',
        related_query_name='user',
    )
    REQUIRED_FIELDS = ['email', 'phone_number', 'birthday'] 
    
    def __str__(self):
        return self.username