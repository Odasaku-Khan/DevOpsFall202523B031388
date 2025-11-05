from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import User
from django.contrib.auth import authenticate

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debug print
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phone_number')
            birthday = data.get('birthday')
            
            print(f"Extracted: {username}, {email}, {phone_number}, {birthday}")  # Debug print
            
            if not all([username, email, password, phone_number]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                birthday=birthday
            )
            
            return JsonResponse({
                'message': 'User created successfully',
                'token': 'your-token-here'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            username = data.get('username')
            password = data.get('password')
            
            if not all([username, password]):
                return JsonResponse({'error': 'Missing username or password'}, status=400)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                return JsonResponse({
                    'message': 'Login successful',
                    'token': 'your-login-token-here'
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)