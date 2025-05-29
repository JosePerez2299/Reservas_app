
from django.http import JsonResponse

def handler404(request):

    return JsonResponse({'error': 'Not Found'}, status=404)