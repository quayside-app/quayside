from django.urls import reverse

def global_context(request):
    """
    Sets context used by EVERY html template
    """
    return {'api_url': '/api/v1'}
        
    