from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import requests

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            try:
                requests.get('http://localhost:11434', timeout=5)
            except requests.RequestException:
                return JsonResponse({'error': 'LLaMA service is not running'}, status=503)
            ollama_url = 'http://localhost:11434/api/generate'
            payload = {
                'model': 'llama3.2',  # Use the correct model
                'prompt': f'You are a helpful chatbot. Respond to: {user_message}',
                'stream': False,
                'temperature': 0.7,
                'max_tokens': 128
            }
            response = requests.post(ollama_url, json=payload, timeout=30)
            print("Ollama status:", response.status_code)
            print("Ollama response:", response.text)
            if response.status_code == 404:
                return JsonResponse({'error': 'Model not found in Ollama'}, status=404)
            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to get response from LLaMA'}, status=500)
            ollama_data = response.json()
            bot_response = ollama_data.get('response', 'Sorry, I could not process your request.')
            return JsonResponse({'response': bot_response.strip()})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'Error connecting to LLaMA: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    def get(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)