# middleware.py

from .models import Visitor
from django.utils.deprecation import MiddlewareMixin

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Simple check to determine device type
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_type = 'mobile'
        else:
            device_type = 'desktop'

        Visitor.objects.create(
            ip_address=ip,
            device_type=device_type,
            user_agent=user_agent
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
