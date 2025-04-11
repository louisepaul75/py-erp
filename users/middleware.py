from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile

class UpdateLastSeenMiddleware(MiddlewareMixin):
    """
    Middleware to update the last_seen timestamp for authenticated users.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                # Update last_seen time
                # Using update avoids race conditions and doesn't call save signals
                UserProfile.objects.filter(user=request.user).update(last_seen=timezone.now())
            except UserProfile.DoesNotExist:
                # This might happen if the profile hasn't been created yet,
                # though the post_save signal should handle this.
                # We can safely ignore this case here.
                pass 
        return None 