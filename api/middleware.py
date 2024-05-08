# api/middleware.py
from django.shortcuts import redirect
from api.models import TermsAndConditions, UserTermsAcceptance

class TermsAndConditionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            latest_terms = TermsAndConditions.objects.order_by("-created_at").first()
            if not latest_terms:
                return self.get_response(request)

            user_terms = UserTermsAcceptance.objects.filter(user=request.user).first()
            if not user_terms or user_terms.accepted_version != latest_terms.version:
                return redirect('terms_and_conditions')

        return self.get_response(request)
